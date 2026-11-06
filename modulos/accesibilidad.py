"""Accesibilidad de Fuente Clara: panel con tamaño de letra, alto contraste y lectura por voz de la página.

Cómo funciona (WCAG 2.2; criterios en DESIGN.md):
- El botón flotante y el panel los crea static/accesibilidad.js directamente en la página (se inserta con st.html y
  JavaScript, sin iframe), así comparten el documento con el resto de la app y con el lector de voz.
- Tamaño de letra: el panel solo cambia la variable --fc-escala-texto; static/estilo.css la usa en los font-size.
- Alto contraste: el control va de 0 a 100 %. Solo en 100 % se activa html[data-fc-contraste="alto"], que redefine
  los mismos tokens de color de la paleta original (static/estilo.css). Sin filtros ni interruptor aparte.
- Lectura por voz: voz.lector_pagina() instala el controlador de voz (static/voz.js) y el panel trae sus botones.
- Se guardan solo el tamaño y el contraste en localStorage. Nunca audio ni textos.
"""
import json
from pathlib import Path

import streamlit as st

from modulos import voz

JS = Path(__file__).resolve().parents[1] / "static" / "accesibilidad.js"


def render_panel(key="lector_global"):
    """Monta el botón flotante de accesibilidad y su panel. Se llama una vez, arriba de la app."""
    voz.lector_pagina(key)
    codigo = voz.incrustar_js(JS.read_text(encoding="utf-8").replace("__LECTOR__", key))
    st.html(f'<div class="fc-instalador" hidden></div><script>{codigo}</script>', unsafe_allow_javascript=True)


# Nombre que usa app.py desde la primera versión del panel.
render_interruptor = render_panel
