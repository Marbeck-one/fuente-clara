"""IA «jueza» (issue #29): segunda revisión de cada respuesta antes de mostrarla.

Complementa la capa 3 del guardrail (reglas fijas, core/guardrail.py): una segunda IA lee lo que se va a mostrar junto
con las citas verificadas y dice si opina, recomienda, toma partido o afirma algo que esas citas no respaldan.

- Se activa con LLM_JUEZA=1 en .env (apagada por defecto: suma una llamada por consulta).
- Puede usar un modelo propio, más barato y rápido: LLM_CADENA_JUEZA=anthropic:claude-haiku-5-5 (ver core/llm.py).
- Si la jueza rechaza, la respuesta no se muestra (se trata como opinión) y el rechazo se cuenta en
  data/votos/bloqueos.jsonl, solo con el motivo, el modelo y la fecha: nunca la pregunta ni la respuesta.
- Si la jueza no responde (error de red o de la API), la respuesta se muestra igual: ya pasó por el filtro, las citas
  verificadas y la capa 3, y la caída de una revisión extra no debe dejar la app sin respuestas. Se avisa en la consola.
"""
import json
import os
import sys
import threading
from datetime import datetime
from pathlib import Path

from core import llm, prompts

ARCHIVO = Path(os.getenv("BLOQUEOS_ARCHIVO") or Path(__file__).resolve().parents[1] / "data" / "votos" / "bloqueos.jsonl")
MOTIVOS = {"opinion": "Opina o valora", "recomendacion": "Recomienda qué hacer o votar", "partidista": "Toma partido político",
           "sin_respaldo": "Afirma algo que las citas no respaldan", "instrucciones": "Muestra sus instrucciones internas",
           "otro": "Otro"}
_candado = threading.Lock()


def activa():
    return os.getenv("LLM_JUEZA", "").strip().lower() in ("1", "true", "si", "sí", "yes")


def _texto_a_revisar(r):
    """Lo que la persona va a leer: respuesta, excepciones, qué cambia, comparaciones y solicitud."""
    partes = []
    for clave, nombre in (("respuesta", "Respuesta"), ("que_cambia", "Qué cambia para ti"), ("organismo", "Organismo sugerido"),
                          ("justificacion", "Justificación"), ("borrador", "Borrador de solicitud")):
        if str(r.get(clave) or "").strip():
            partes.append(f"{nombre}: {r[clave]}")
    for e in r.get("excepciones") or []:
        partes.append(f"Excepción: {e}")
    for c in r.get("comparaciones") or []:
        if c.get("texto_oficial"):
            partes.append(f"Comparación [{c.get('etiqueta')}]: {c['texto_oficial']}")
    return "\n".join(partes)


def _citas(r):
    citas = list(r.get("citas_mostrar") or []) or [c for c in r.get("citas") or [] if c.get("verificada")]
    for c in r.get("comparaciones") or []:
        citas += [x for x in c.get("citas") or [] if x.get("verificada")]
    return "\n".join(f"- {c.get('articulo')}, pág. {c.get('pagina')}: «{c.get('texto_literal')}»" for c in citas) or "(sin citas)"


def _registrar(motivo):
    proveedor, modelo = llm.ultimo_modelo()
    try:
        ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
        with _candado, ARCHIVO.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"fecha": datetime.now().isoformat(timespec="seconds"), "capa": "jueza", "motivo": motivo,
                                "proveedor": proveedor, "modelo": modelo, "version": prompts.VERSION}, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[Fuente Clara] No se pudo registrar el bloqueo de la jueza: {e}", file=sys.stderr)


def revisar(r):
    """Devuelve None si aprueba (o si está apagada o no responde) y el motivo si rechaza."""
    texto = _texto_a_revisar(r)
    if not activa() or not texto:
        return None
    anterior = getattr(llm._hilo, "ultimo", None)  # la traza del voto debe nombrar al modelo que respondió, no a la jueza
    try:
        datos = llm.complete(prompts.JUEZA, f"CITAS VERIFICADAS DEL DOCUMENTO:\n{_citas(r)}\n\nTEXTO A REVISAR:\n{texto}", tarea="jueza")
    except llm.ErrorLLM as e:
        print(f"[Fuente Clara] La jueza no respondió; se muestra la respuesta sin segunda revisión: {e}", file=sys.stderr)
        return None
    finally:
        llm._hilo.ultimo = anterior
    if str(datos.get("aprobada")).strip().lower() == "true":
        return None
    motivo = str(datos.get("motivo", "otro")).strip().lower()
    motivo = motivo if motivo in MOTIVOS else "otro"
    _registrar(motivo)
    return motivo


def leer():
    """Los rechazos registrados (motivo, modelo, versión y fecha)."""
    if not ARCHIVO.exists():
        return []
    with ARCHIVO.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]
