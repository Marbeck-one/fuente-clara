"""Lectura en voz alta de las respuestas (issue #5). Usa la voz del propio navegador (Web Speech API).

Qué hace este módulo:
- `boton_escuchar(texto, key=None)` dibuja los botones Escuchar / Pausar / Continuar / Detener. Cualquier módulo lo llama
  con el texto ya preparado. La lógica de reproducción está una sola vez, en static/voz.js.
- `texto_explicame`, `texto_verifica` y `texto_estado` arman en Python lo que se lee a partir de la misma respuesta que se
  muestra: solo la respuesta y sus citas verificadas, sin menús, botones, HTML, Markdown ni enlaces.

Además, `boton_dictar(destino)` permite dictar la pregunta (issue #6): usa el reconocimiento de voz del navegador
(static/dictado.js) y escribe la transcripción en el campo, para que la persona la revise antes de enviar.

Privacidad: el texto va de Python al navegador dentro de la página y se lee con `speechSynthesis`. Esta app no llama a ninguna
API de voz ni a la IA, no guarda audio y no usa localStorage. Ojo: según el dispositivo, la voz del sistema puede ser
de red (por ejemplo, algunas voces de Google en Chrome); eso lo decide el navegador, no Fuente Clara.
"""
import hashlib
import json
import re
from html import escape
from pathlib import Path

import streamlit as st

JS = Path(__file__).resolve().parents[1] / "static" / "voz.js"
JS_DICTADO = Path(__file__).resolve().parents[1] / "static" / "dictado.js"

_BOTONES = [("escuchar", "Escuchar respuesta", "Escuchar la respuesta en voz alta"),
            ("pausar", "Pausar", "Pausar la lectura"),
            ("continuar", "Continuar", "Continuar la lectura"),
            ("detener", "Detener", "Detener la lectura")]


def incrustar_js(codigo):
    """Devuelve el código listo para ir dentro de <script> en st.html.

    Streamlit limpia el HTML con DOMPurify, que elimina todo <script> cuyo texto contenga algo parecido a una etiqueta
    (`<div`, `</p>`...). Por eso el `<` de las etiquetas que arma el JavaScript se escribe como \\u003C, que dentro de un
    texto de JavaScript vale exactamente lo mismo. El código de los .js no debe usar `<` pegado a una letra como operador.
    """
    return re.sub(r"<(?=[/!A-Za-z])", lambda _: "\\u003C", codigo)


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
    botones = "".join(  # el ícono de cada botón lo dibuja el CSS (st.html elimina los <svg>)
        f'<button type="button" data-fc-accion="{accion}" aria-label="{escape(descripcion)}"'
        f'{"" if accion == "escuchar" else " hidden"}><span>{escape(etiqueta)}</span></button>'
        for accion, etiqueta, descripcion in _BOTONES)
    return (f'<div class="fc-voz" role="group" aria-label="Lectura en voz alta" data-estado="inactivo" '
            f'data-fc-voz-id="{huella}" data-fc-texto="{escape(texto, quote=True)}">'
            f'<div class="fc-voz-botones">{botones}</div>'
            f'<span class="fc-voz-estado" role="status" aria-live="polite"></span></div>'
            f'<script>{incrustar_js(JS.read_text(encoding="utf-8"))}</script>')


def boton_escuchar(texto, key=None):
    """Botón «Escuchar respuesta» con pausa, continuar y detener. `texto` es lo único que se lee.

    `key` distingue dos botones con el mismo texto. Si el texto no cambia entre reruns, la lectura sigue sin reiniciarse.
    No hace nada si no hay texto que leer.
    """
    texto = limpiar(texto)
    if texto:
        st.html(_html(texto, key), unsafe_allow_javascript=True)


# ---------- lector de página completa ----------

def lector_pagina(key="lector_global"):
    """Instala el controlador de voz de la página (static/voz.js) y le da nombre al lector de página completa.

    Los botones «Leer página completa», Pausar, Continuar y Detener los trae el panel de accesibilidad
    (modulos/accesibilidad.py). Comparten el controlador con «Escuchar respuesta»: nunca suenan dos a la vez, y
    empezar uno corta el otro. Lo que se lee sale del contenido visible de la pestaña actual (títulos, explicaciones,
    respuestas, citas verificadas y avisos); ver `recolectar` en static/voz.js. No hace nada hasta que la persona toca el botón.
    """
    codigo = f"window.__fcVozPagina = {json.dumps(key)};" + chr(10) + incrustar_js(JS.read_text(encoding="utf-8"))
    st.html(f'<div class="fc-instalador" hidden></div><script>{codigo}</script>', unsafe_allow_javascript=True)


# ---------- dictado por micrófono (issue #6) ----------

def _html_dictado(destino):
    botones = (
        '<button type="button" data-fc-accion="dictar" aria-label="Dictar con el micrófono"><span>Dictar con el micrófono</span></button>'
        '<button type="button" data-fc-accion="parar" aria-label="Terminar el dictado" hidden><span>Terminar dictado</span></button>')
    return (f'<div class="fc-dictado" role="group" aria-label="Dictado por micrófono" data-estado="inactivo" '
            f'data-fc-destino="{escape(destino, quote=True)}">'
            f'<div class="fc-dictado-botones">{botones}</div>'
            f'<span class="fc-dictado-estado" role="status" aria-live="polite"></span>'
            f'<p class="fc-dictado-aviso">El dictado usa el reconocimiento de voz de tu navegador: el audio puede enviarse al '
            f'servicio de voz del navegador (en Chrome, Google). Fuente Clara no lo guarda.</p></div>'
            f'<script>{incrustar_js(JS_DICTADO.read_text(encoding="utf-8"))}</script>')


def boton_dictar(destino):
    """Botón «Dictar con el micrófono» para el campo de texto cuya etiqueta es `destino` (por ejemplo, «Tu pregunta»).

    La transcripción se escribe en ese campo y la persona la revisa antes de enviar. Fuente Clara no recibe ni guarda
    el audio; el reconocimiento lo hace el navegador (en Chrome, con el servicio de voz de Google).
    """
    st.html(_html_dictado(destino), unsafe_allow_javascript=True)
