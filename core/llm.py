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


def _respetar_intervalo():
    # Para APIs gratuitas con límite de velocidad: LLM_INTERVALO_MIN = segundos mínimos entre llamadas.
    intervalo = float(os.getenv("LLM_INTERVALO_MIN", "0") or 0)
    time.sleep(max(0.0, intervalo - (time.time() - _ultima_llamada[0])))


def _llamar(system, user):
    _respetar_intervalo()
    try:
        return _llamar_proveedor(system, user)
    finally:
        _ultima_llamada[0] = time.time()


def _llamar_proveedor(system, user):
    # El cliente se guarda en una variable: google-genai cierra su conexión si el cliente se descarta antes de la llamada.
    proveedor, modelo = configuracion()
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
        model=modelo, contents=user,
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


def complete(system, user):
    """Pide al modelo una respuesta JSON y la devuelve como dict. Reintenta una vez si falla."""
    system += INSTRUCCION_JSON
    error = None
    for _ in range(2):
        nota = ("\n\nIMPORTANTE: tu respuesta anterior no era JSON válido. Responde solo con el objeto JSON."
                if isinstance(error, ValueError) else "")
        try:
            return _parsear(_llamar(system, user + nota))
        except ErrorLLM:
            raise
        except Exception as e:  # error de red, de API o JSON inválido
            error = e
    raise ErrorLLM(f"{type(error).__name__}: {str(error)[:200]}")
