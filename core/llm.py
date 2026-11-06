"""Capa LLM intercambiable, con cadena de modelos de respaldo (archivo .env).

- Un solo modelo: LLM_PROVIDER y LLM_MODEL.
- Varios, en orden: LLM_CADENA=anthropic:claude-sonnet-5-5,groq:openai/gpt-oss-120b,...
  Si un modelo falla o se satura, se pasa al siguiente. Los saturados (429) se saltan 45 s y los que
  tienen clave o nombre inválido, 10 min. Mismo criterio que los prototipos de referencia del Desafío 3.

No registra ni guarda lo que escribe el usuario.
"""
import base64
import io
import json
import os
import re
import sys
import threading
import time

from dotenv import load_dotenv

load_dotenv()

MODELOS_POR_DEFECTO = {
    "anthropic": "claude-haiku-5-5",
    "openai": "gpt-4.1-mini",
    "google": "gemini-2.5-flash",
}
# Proveedores compatibles con la API de OpenAI: dirección y variable de su clave.
COMPATIBLES_OPENAI = {
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "mistral": ("https://api.mistral.ai/v1", "MISTRAL_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "cerebras": ("https://api.cerebras.ai/v1", "CEREBRAS_API_KEY"),
    "together": ("https://api.together.xyz/v1", "TOGETHER_API_KEY"),
    "deepseek": ("https://api.deepseek.com", "DEEPSEEK_API_KEY"),
}
CLAVES = {
    "anthropic": ("ANTHROPIC_API_KEY",),
    "openai": ("OPENAI_API_KEY",),
    "google": ("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    **{p: (variable,) for p, (_, variable) in COMPATIBLES_OPENAI.items()},
}
LEEN_IMAGENES = {"google", "anthropic"}
MAX_BYTES_IMAGEN = 5 * 1024 * 1024  # Anthropic acepta hasta 5 MB por imagen
PAUSA_SATURADO, PAUSA_INVALIDO = 45, 600  # segundos que se salta un modelo saturado o con clave/modelo inválido
INSTRUCCION_JSON = "\n\nResponde ÚNICAMENTE con un objeto JSON válido, sin texto adicional ni bloques de código."
SIN_IMAGENES = "La lectura de imágenes requiere un modelo de Google o Anthropic (LLM_PROVIDER o LLM_CADENA)."


class ErrorLLM(Exception):
    """El modelo no respondió o su respuesta no se pudo interpretar."""


def _eslabon(proveedor, modelo):
    proveedor = proveedor.strip().lower()
    if proveedor not in CLAVES:
        raise ErrorLLM(f"Proveedor no válido: '{proveedor}'. Usa uno de: {', '.join(CLAVES)}.")
    modelo = modelo.strip() or MODELOS_POR_DEFECTO.get(proveedor, "")
    if not modelo:
        raise ErrorLLM(f"Falta el modelo de '{proveedor}' (formato proveedor:modelo).")
    return proveedor, modelo


def cadena():
    """Lista ordenada de (proveedor, modelo) que se prueban. Sin LLM_CADENA es un solo modelo."""
    texto = os.getenv("LLM_CADENA", "").strip()
    if not texto:
        return [_eslabon(os.getenv("LLM_PROVIDER", "anthropic"), os.getenv("LLM_MODEL", ""))]
    # Solo el primer ":" separa: el nombre del modelo puede traer otros (por ejemplo, qwen2.5:7b).
    return [_eslabon(*(parte.split(":", 1) + [""])[:2]) for parte in texto.split(",") if parte.strip()]


def configuracion():
    """Devuelve (proveedor, modelo) del modelo principal: el primero de la cadena."""
    return cadena()[0]


def tiene_clave(proveedor):
    return any(os.getenv(v, "").strip() for v in CLAVES[proveedor])


def soporta_imagenes():
    """True si algún modelo de la cadena puede leer capturas."""
    return any(proveedor in LEEN_IMAGENES for proveedor, _ in cadena())


# --- Modelos en pausa: compartido entre todas las sesiones de la app ---------------------------
_pausas = {}
_candado = threading.Lock()


def _pausar(eslabon, segundos):
    with _candado:
        _pausas[eslabon] = time.time() + segundos


def pausado(eslabon):
    return _pausas.get(eslabon, 0) > time.time()


# --- Qué modelo respondió: uno por hilo, porque cada sesión de Streamlit corre en el suyo -------
_hilo = threading.local()


def ultimo_modelo():
    """(proveedor, modelo) que respondió la última llamada de este hilo; si no hubo, el principal."""
    return getattr(_hilo, "ultimo", None) or configuracion()


def _opcionales(modelo=""):
    # La temperatura es opcional porque algunos modelos nuevos no la aceptan.
    # Claude Haiku 5.5 no tiene temperatura configurable, así que nunca se envía.
    if modelo.startswith("claude-haiku-5"):
        return {}
    temperatura = os.getenv("LLM_TEMPERATURE", "").strip()
    return {"temperature": float(temperatura)} if temperatura else {}


def _timeout():
    """Segundos máximos de espera por llamada, o None para usar el valor del cliente."""
    valor = os.getenv("LLM_TIMEOUT", "").strip()
    return float(valor) if valor else None


def _max_tokens():
    """Máximo de tokens de salida. Acota el costo de cada respuesta."""
    valor = os.getenv("LLM_MAX_TOKENS", "").strip()
    return int(valor) if valor else 3000


_ultima_llamada = [0.0]
_espera_total = [0.0]


def _respetar_intervalo():
    # Para APIs gratuitas con límite de velocidad: LLM_INTERVALO_MIN = segundos mínimos entre llamadas.
    intervalo = float(os.getenv("LLM_INTERVALO_MIN", "0") or 0)
    pausa = max(0.0, intervalo - (time.time() - _ultima_llamada[0]))
    _espera_total[0] += pausa
    time.sleep(pausa)


def segundos_esperados():
    """Segundos que se esperó por LLM_INTERVALO_MIN. scripts/evaluar.py los descuenta del tiempo de respuesta."""
    return _espera_total[0]


def _contenido_google(user, imagen):
    """La imagen va primero; google-genai la convierte a inlineData en base64."""
    return [imagen, user] if imagen is not None else user


def _imagen_jpeg_base64(imagen):
    """Codifica la captura en JPEG base64. Se usa solo para la petición; nunca se guarda."""
    salida = io.BytesIO()
    imagen.save(salida, format="JPEG", quality=92)
    datos = salida.getvalue()
    if len(datos) > MAX_BYTES_IMAGEN:
        raise ErrorLLM("La imagen es demasiado grande para enviarla al modelo.")
    return base64.standard_b64encode(datos).decode("ascii")


def _contenido_anthropic(user, imagen):
    """Anthropic recibe la imagen como bloque base64 antes del texto."""
    if imagen is None:
        return user
    return [
        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                     "data": _imagen_jpeg_base64(imagen)}},
        {"type": "text", "text": user},
    ]


def _llamar(system, user, imagen=None, eslabon=None, reintentos=True):
    _respetar_intervalo()
    try:
        return _llamar_proveedor(system, user, imagen, eslabon, reintentos)
    finally:
        _ultima_llamada[0] = time.time()


def _llamar_proveedor(system, user, imagen=None, eslabon=None, reintentos=True):
    """Una llamada a un modelo. Con `reintentos=False` (en cadena) los SDK no reintentan por su cuenta,
    así se pasa rápido al siguiente modelo."""
    # El cliente se guarda en una variable: google-genai cierra su conexión si el cliente se descarta antes de la llamada.
    proveedor, modelo = eslabon or configuracion()
    if imagen is not None and proveedor not in LEEN_IMAGENES:
        raise ErrorLLM(SIN_IMAGENES)
    timeout = _timeout()
    max_tokens = _max_tokens()
    opciones = ({"timeout": timeout} if timeout else {}) | ({} if reintentos else {"max_retries": 0})
    if proveedor == "anthropic":
        import anthropic
        cliente = anthropic.Anthropic(**opciones)
        r = cliente.messages.create(
            model=modelo, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": _contenido_anthropic(user, imagen)}],
            **_opcionales(modelo))
        return "".join(b.text for b in r.content if b.type == "text")
    if proveedor == "google":
        from google import genai
        from google.genai import types
        cliente = genai.Client()
        # En google-genai el timeout de HttpOptions se expresa en milisegundos.
        http_options = types.HttpOptions(timeout=int(timeout * 1000)) if timeout else None
        r = cliente.models.generate_content(
            model=modelo, contents=_contenido_google(user, imagen),
            config=types.GenerateContentConfig(
                system_instruction=system, response_mime_type="application/json",
                max_output_tokens=max_tokens, http_options=http_options, **_opcionales(modelo)))
        return r.text or ""
    # openai y los compatibles (groq, mistral…): mismo cliente, cambian la dirección y la clave.
    from openai import OpenAI
    if proveedor in COMPATIBLES_OPENAI:
        url, variable = COMPATIBLES_OPENAI[proveedor]
        opciones |= {"base_url": url, "api_key": os.getenv(variable, "")}
    cliente = OpenAI(**opciones)
    r = cliente.chat.completions.create(
        model=modelo, max_tokens=max_tokens, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        **_opcionales(modelo))
    return r.choices[0].message.content or ""


def _parsear(texto):
    texto = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
    inicio, fin = texto.find("{"), texto.rfind("}")
    if inicio == -1 or fin == -1:
        raise ValueError("La respuesta no contiene JSON.")
    datos = json.loads(texto[inicio:fin + 1])
    if not isinstance(datos, dict):
        raise ValueError("El JSON no es un objeto.")
    return datos


def _codigo_http(error):
    """Código HTTP de un error de cualquiera de los tres SDK (anthropic, openai, google-genai)."""
    for atributo in ("status_code", "code"):
        valor = getattr(error, atributo, None)
        if isinstance(valor, int):
            return valor
    return None


def complete(system, user, imagen=None):
    """Pide al modelo una respuesta JSON y la devuelve como dict.

    Con un solo modelo, reintenta hasta 3 veces si falla, con una espera creciente. Con una cadena, prueba los modelos en orden
    (primero los que no están en pausa): uno que falla cede su turno al siguiente, y uno que responde
    algo que no es JSON tiene una segunda oportunidad. Si todos fallan, lanza ErrorLLM con el motivo
    de cada uno (nunca con el texto de la persona).

    `imagen` es un PIL.Image.Image opcional. Se envía en la misma petición que el texto y
    nunca se guarda ni se registra. Solo se prueban los modelos que leen imágenes.
    """
    system += INSTRUCCION_JSON
    eslabones = cadena()
    if imagen is not None and len(eslabones) > 1:  # con un solo modelo, _llamar_proveedor avisa si no lee imágenes
        eslabones = [e for e in eslabones if e[0] in LEEN_IMAGENES]
        if not eslabones:
            raise ErrorLLM(SIN_IMAGENES)
    varios = len(eslabones) > 1
    errores = []
    for e in [x for x in eslabones if not pausado(x)] or eslabones:
        if varios and not tiene_clave(e[0]):
            errores.append(f"{e[0]}/{e[1]}: falta {' o '.join(CLAVES[e[0]])}")
            continue
        error = None
        intentos = 2 if varios else 3
        for intento in range(intentos):
            nota = ("\n\nIMPORTANTE: tu respuesta anterior no era JSON válido. Responde solo con el objeto JSON."
                    if isinstance(error, ValueError) else "")
            try:
                datos = _parsear(_llamar(system, user + nota, imagen, e, reintentos=not varios))
                _hilo.ultimo = e
                return datos
            except ErrorLLM:
                raise
            except Exception as err:  # error de red, de API o JSON inválido
                error = err
                codigo = _codigo_http(err)
                if codigo == 429:
                    _pausar(e, PAUSA_SATURADO)
                elif codigo in (401, 403, 404):
                    _pausar(e, PAUSA_INVALIDO)
                if varios and not isinstance(err, ValueError):
                    break  # en cadena: el siguiente modelo, en vez de insistir con este
                if not varios and intento < intentos - 1:
                    time.sleep(1.5 * (intento + 1))  # un solo modelo: esperar un poco antes de insistir
        errores.append(f"{e[0]}/{e[1]}: {type(error).__name__} {str(error)[:160]}")
        if varios:
            print(f"[llm] {errores[-1]}", file=sys.stderr, flush=True)
    raise ErrorLLM(" | ".join(errores)[:600])
