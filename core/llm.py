"""Capa LLM intercambiable: proveedor en LLM_PROVIDER y modelo en LLM_MODEL (archivo .env).

No registra ni guarda lo que escribe el usuario.
"""
import json
import os
import re
import time

from dotenv import load_dotenv

load_dotenv()

MODELOS_POR_DEFECTO = {
    "anthropic": "claude-sonnet-5-5",
    "openai": "gpt-4.1-mini",
    "google": "gemini-2.5-flash",
}
INSTRUCCION_JSON = "\n\nResponde ÚNICAMENTE con un objeto JSON válido, sin texto adicional ni bloques de código."


class ErrorLLM(Exception):
    """El modelo no respondió o su respuesta no se pudo interpretar."""


def configuracion():
    """Devuelve (proveedor, modelo) según el .env."""
    proveedor = os.getenv("LLM_PROVIDER", "anthropic").strip().lower()
    if proveedor not in MODELOS_POR_DEFECTO:
        raise ErrorLLM(f"LLM_PROVIDER no válido: '{proveedor}'. Usa anthropic, openai o google.")
    return proveedor, os.getenv("LLM_MODEL", "").strip() or MODELOS_POR_DEFECTO[proveedor]


def _opcionales():
    # La temperatura es opcional porque algunos modelos nuevos no la aceptan.
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


def _llamar(system, user, imagen=None):
    _respetar_intervalo()
    try:
        return _llamar_proveedor(system, user, imagen)
    finally:
        _ultima_llamada[0] = time.time()


def _llamar_proveedor(system, user, imagen=None):
    # El cliente se guarda en una variable: google-genai cierra su conexión si el cliente se descarta antes de la llamada.
    proveedor, modelo = configuracion()
    if imagen is not None and proveedor != "google":
        raise ErrorLLM("La lectura de imágenes requiere LLM_PROVIDER=google.")
    timeout = _timeout()
    max_tokens = _max_tokens()
    if proveedor == "anthropic":
        import anthropic
        cliente = anthropic.Anthropic(timeout=timeout) if timeout else anthropic.Anthropic()
        r = cliente.messages.create(
            model=modelo, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}], **_opcionales())
        return "".join(b.text for b in r.content if b.type == "text")
    if proveedor == "openai":
        from openai import OpenAI
        cliente = OpenAI(timeout=timeout) if timeout else OpenAI()
        r = cliente.chat.completions.create(
            model=modelo, max_tokens=max_tokens, response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            **_opcionales())
        return r.choices[0].message.content or ""
    from google import genai
    from google.genai import types
    cliente = genai.Client()
    # En google-genai el timeout de HttpOptions se expresa en milisegundos.
    http_options = types.HttpOptions(timeout=int(timeout * 1000)) if timeout else None
    r = cliente.models.generate_content(
        model=modelo, contents=_contenido_google(user, imagen),
        config=types.GenerateContentConfig(
            system_instruction=system, response_mime_type="application/json",
            max_output_tokens=max_tokens, http_options=http_options, **_opcionales()))
    return r.text or ""


def _parsear(texto):
    texto = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
    inicio, fin = texto.find("{"), texto.rfind("}")
    if inicio == -1 or fin == -1:
        raise ValueError("La respuesta no contiene JSON.")
    datos = json.loads(texto[inicio:fin + 1])
    if not isinstance(datos, dict):
        raise ValueError("El JSON no es un objeto.")
    return datos


def complete(system, user, imagen=None):
    """Pide al modelo una respuesta JSON y la devuelve como dict. Reintenta una vez si falla.

    `imagen` es un PIL.Image.Image opcional. Se envía en la misma petición que el texto y
    nunca se guarda ni se registra.
    """
    system += INSTRUCCION_JSON
    error = None
    for _ in range(2):
        nota = ("\n\nIMPORTANTE: tu respuesta anterior no era JSON válido. Responde solo con el objeto JSON."
                if isinstance(error, ValueError) else "")
        try:
            return _parsear(_llamar(system, user + nota, imagen))
        except ErrorLLM:
            raise
        except Exception as e:  # error de red, de API o JSON inválido
            error = e
    raise ErrorLLM(f"{type(error).__name__}: {str(error)[:200]}")
