"""Votos sobre las respuestas: miden si son buenas y con qué modelo e instrucciones salieron.

Cada voto guarda solo su contexto: pestaña, perfil, citas verificadas, modelo y versión de las instrucciones.
La pregunta y la respuesta se guardan SOLO si la persona lo autoriza al votar 👎, y antes se ocultan
RUT, correos y teléfonos. El archivo está en .gitignore: nunca se sube al repositorio.
"""
import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path

from core import filtro, prompts
from core.citas import hay_verificada
from core.llm import configuracion

ARCHIVO = Path(os.getenv("VOTOS_ARCHIVO") or Path(__file__).resolve().parents[1] / "data" / "votos" / "votos.jsonl")
MOTIVOS = ["No responde lo que pregunté", "Difícil de entender", "La cita no respalda la respuesta", "Suena a opinión"]
_candado = threading.Lock()  # varias personas pueden votar a la vez

_DATOS_PERSONALES = [
    (re.compile(r"(?<!\d)\d{1,2}\.?\d{3}\.?\d{3}-[\dkK](?![\w])"), "[RUT]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[CORREO]"),
    (re.compile(r"(?:\+?56[\s.-]?)?(?<!\d)[29](?:[\s.-]?\d){8}(?!\d)"), "[TELÉFONO]"),  # celulares y fijos
]


def traza():
    """Con qué se generó una respuesta."""
    proveedor, modelo = configuracion()
    return {"proveedor": proveedor, "modelo": modelo, "version": prompts.VERSION}


def ocultar_datos(texto):
    for patron, reemplazo in _DATOS_PERSONALES:
        texto = patron.sub(reemplazo, texto)
    return texto


def citas_de(r):
    """Todas las citas de un resultado (en Verifica vienen dentro de cada comparación)."""
    return list(r.get("citas") or []) + [c for comp in r.get("comparaciones") or [] for c in comp["citas"]]


def resumen(r):
    """La respuesta como texto simple, para que el equipo la revise."""
    if r["categoria"] == filtro.OPINION:
        return "(El filtro la rechazó: Fuente Clara no opina.)"
    if "comparaciones" in r:
        lineas = [f"- {c['afirmacion']} → [{c['etiqueta'] or 'sin etiqueta'}] {c['texto_oficial']}"
                  for c in r["comparaciones"]]
        return "\n".join(lineas) or "(No encontró afirmaciones para comparar.)"
    if "borrador" in r:
        return f"Organismo sugerido: {r['organismo']}\n{r['justificacion']}\n\n{r['borrador']}"
    if r["categoria"] == filtro.FUERA:
        return "(El documento no responde esta pregunta.)"
    texto = r.get("respuesta", "")
    if r.get("que_cambia") and r.get("perfil") not in (None, "ninguno"):
        texto += f"\n\nQué cambia para ti ({r['perfil']}): {r['que_cambia']}"
    if not hay_verificada(r.get("citas") or []):
        texto = "(No se le mostró a la persona: no tenía cita verificada.)\n" + texto
    return texto


def _guardar(registro):
    ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
    with _candado, ARCHIVO.open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def votar(r, pestana, bueno):
    """Guarda el voto con su contexto. Nunca guarda la pregunta ni la respuesta."""
    citas = citas_de(r)
    _guardar({"tipo": "voto", "id": r["id"], "fecha": datetime.now().isoformat(timespec="seconds"),
              "documento": r.get("documento"), "pestana": pestana, "perfil": r.get("perfil") or "ninguno",
              "categoria": r["categoria"], "citas_total": len(citas),
              "citas_verificadas": sum(bool(c["verificada"]) for c in citas),
              **r["traza"], "voto": "bueno" if bueno else "malo"})


def detallar(r, motivo, autoriza):
    """Agrega el motivo del 👎. Solo si la persona autoriza, guarda la pregunta y la respuesta."""
    registro = {"tipo": "detalle", "id": r["id"], "motivo": motivo, "autoriza": bool(autoriza)}
    if autoriza:
        registro.update(
            pregunta=ocultar_datos(r["entrada"]), respuesta=ocultar_datos(resumen(r)),
            citas=[{k: c[k] for k in ("articulo", "pagina", "texto_literal", "verificada")} for c in citas_de(r)])
    _guardar(registro)


def leer():
    """Todos los votos, cada uno unido a su detalle si lo tiene."""
    if not ARCHIVO.exists():
        return []
    votos, detalles = {}, {}
    for linea in ARCHIVO.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(linea)
        except json.JSONDecodeError:
            continue
        (votos if d.get("tipo") == "voto" else detalles)[d.get("id")] = d
    return [{**v, **{k: x for k, x in detalles.get(i, {}).items() if k not in ("tipo", "id")}}
            for i, v in votos.items()]
