"""Lectura en voz alta de las respuestas (issue #5). Usa la voz del propio navegador (Web Speech API).

Qué hace este módulo:
- `boton_escuchar(texto, key=None)` dibuja los botones Escuchar / Pausar / Continuar / Detener. Cualquier módulo lo llama
  con el texto ya preparado. La lógica de reproducción está una sola vez, en static/voz.js.
- `texto_explicame`, `texto_verifica` y `texto_estado` arman en Python lo que se lee a partir de la misma respuesta que se
  muestra: solo la respuesta y sus citas verificadas, sin menús, botones, HTML, Markdown ni enlaces.

Privacidad: el texto va de Python al navegador dentro de la página y se lee con `speechSynthesis`. Esta app no llama a ninguna
API de voz ni a la IA, no guarda audio y no usa localStorage. Ojo: según el dispositivo, la voz del sistema puede ser
de red (por ejemplo, algunas voces de Google en Chrome); eso lo decide el navegador, no Fuente Clara.
"""
import hashlib
import re
from html import escape
from pathlib import Path

import streamlit as st

JS = Path(__file__).resolve().parents[1] / "static" / "voz.js"

_ICONO = {  # SVG simples y decorativos (el nombre accesible lo da el texto del botón)
    "escuchar": '<path d="M3 10v4h4l5 4V6L7 10H3z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18 6a8.5 8.5 0 0 1 0 12" '
                'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "pausar": '<path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"/>',
    "continuar": '<path d="M8 5v14l11-7z"/>',
    "detener": '<path d="M6 6h12v12H6z"/>',
}
_BOTONES = [("escuchar", "Escuchar respuesta", "Escuchar la respuesta en voz alta"),
            ("pausar", "Pausar", "Pausar la lectura"),
            ("continuar", "Continuar", "Continuar la lectura"),
            ("detener", "Detener", "Detener la lectura")]


# ---------- texto que se lee ----------

def limpiar(texto):
    """Deja solo lo que se dice en voz alta: sin Markdown, HTML ni enlaces."""
    t = str(texto or "")
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)                 # imágenes
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)              # enlaces: queda su texto
    t = re.sub(r"<[^>]+>", " ", t)                              # etiquetas HTML
    t = re.sub(r"(https?://|www\.)\S+", " ", t)                 # URLs
    t = re.sub(r"^\s{0,3}#{1,6}\s*", "", t, flags=re.M)         # títulos Markdown
    t = re.sub(r"^\s*[-*+•]\s+", "", t, flags=re.M)             # viñetas
    t = re.sub(r"[*_`~>|]+", "", t)                             # énfasis, código, citas
    t = t.replace("[", "").replace("]", "")
    return re.sub(r"\s+", " ", t).strip()


def _termina(frase):
    frase = frase.strip()
    return frase if not frase or frase[-1] in ".!?:;" else frase + "."


def _citas(citas):
    """Solo las citas verificadas, con su artículo y página, tal como se muestran en pantalla."""
    partes = []
    for c in citas or []:
        if c.get("verificada"):
            partes.append(f"Cita del {limpiar(c['articulo'])}, página {c['pagina']}. El documento dice: "
                          f"{_termina(limpiar(c['texto_literal']))}")
    return partes


def texto_explicame(r):
    partes = [_termina(limpiar(r.get("respuesta")))]
    if r.get("que_cambia") and r.get("perfil") != "ninguno":
        partes.append(f"Qué cambia para ti, {limpiar(r.get('perfil'))}. {_termina(limpiar(r['que_cambia']))}")
    citas = _citas(r.get("citas"))
    if citas:
        partes.append("De dónde sale.")
        partes += citas
    return " ".join(p for p in partes if p)


def texto_verifica(r, es_valida, etiquetas):
    """`es_valida` y `etiquetas` vienen de modulos/verifica.py: se lee solo lo que la pantalla muestra como válido."""
    partes = []
    for i, c in enumerate(r.get("comparaciones") or [], 1):
        if not es_valida(c):
            continue
        etiqueta = re.sub(r"^\W+", "", etiquetas[c["etiqueta"]])  # sin los símbolos ＝ ≠ ∅
        partes.append(f"Comparación {i}. La afirmación dice: {_termina(limpiar(c['afirmacion']))} "
                      f"{_termina(etiqueta)} Lo que dice el texto oficial: {_termina(limpiar(c['texto_oficial']))}")
        partes += _citas(c.get("citas"))
    if partes:
        partes.append("Fuente Clara no dice quién tiene razón. Tú comparas y decides.")
    return " ".join(partes)


def texto_estado(r, cfg):
    """Organismo sugerido, borrador, y los pasos y plazos tal como los muestra la pantalla."""
    partes = [f"Organismo sugerido: {_termina(limpiar(r.get('organismo')))}", _termina(limpiar(r.get("justificacion")))]
    partes += _citas(r.get("citas"))
    partes.append(f"Borrador de solicitud. {_termina(limpiar(r.get('borrador')))}")
    for titulo, clave in (("Pasos", "pasos"), ("Plazos", "plazos")):
        items = []
        for i, item in enumerate(cfg.get(clave) or [], 1):
            texto = _termina(limpiar(item["texto"])) + (" Por verificar." if item.get("estado") == "VERIFICAR" else "")
            items.append(f"{i}. {texto}" if clave == "pasos" else texto)
        if items:
            partes.append(f"{titulo}. " + " ".join(items))
    partes.append("Tú decides si envías la solicitud en el Portal de Transparencia.")
    return " ".join(p for p in partes if p)


# ---------- botón ----------

def _html(texto, key):
    huella = hashlib.sha1(f"{key or ''}|{texto}".encode("utf-8")).hexdigest()[:12]
    botones = "".join(
        f'<button type="button" data-fc-accion="{accion}" aria-label="{escape(descripcion)}"'
        f'{"" if accion == "escuchar" else " hidden"}>'
        f'<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">'
        f'{_ICONO[accion]}</svg><span>{escape(etiqueta)}</span></button>'
        for accion, etiqueta, descripcion in _BOTONES)
    return (f'<div class="fc-voz" role="group" aria-label="Lectura en voz alta" data-estado="inactivo" '
            f'data-fc-voz-id="{huella}" data-fc-texto="{escape(texto, quote=True)}">'
            f'<div class="fc-voz-botones">{botones}</div>'
            f'<span class="fc-voz-estado" role="status" aria-live="polite"></span></div>'
            f'<script>{JS.read_text(encoding="utf-8")}</script>')


def boton_escuchar(texto, key=None):
    """Botón «Escuchar respuesta» con pausa, continuar y detener. `texto` es lo único que se lee.

    `key` distingue dos botones con el mismo texto. Si el texto no cambia entre reruns, la lectura sigue sin reiniciarse.
    No hace nada si no hay texto que leer.
    """
    texto = limpiar(texto)
    if texto:
        st.html(_html(texto, key), unsafe_allow_javascript=True)
