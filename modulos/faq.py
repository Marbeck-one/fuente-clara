"""Dudas comunes: respuestas preparadas y revisadas por el equipo. No llaman a la IA ni guardan nada."""
from pathlib import Path

import streamlit as st
import yaml

from core.citas import verificar
from modulos.comun import mostrar_citas

CARPETA = Path(__file__).resolve().parents[1] / "data" / "faq"


def leer(doc):
    """Todas las dudas del archivo del documento (mismo nombre que el documento, en data/faq/), con sus citas verificadas."""
    ruta = CARPETA / f"{Path(doc['archivo']).stem}.yaml"
    if not ruta.exists():
        return []
    dudas = yaml.safe_load(ruta.read_text(encoding="utf-8")) or []
    for duda in dudas:
        for parte in duda["respuesta"]:
            parte["cita_verificada"] = verificar([{"texto_literal": parte["cita"]}], doc)[0]
    return dudas


def publicables(doc):
    """Solo las revisadas por una persona y con todas sus citas en el documento: una frase sola podría cambiar el sentido."""
    return [d for d in leer(doc) if d.get("revisada") is True
            and all(p["cita_verificada"]["verificada"] for p in d["respuesta"])]


def _alternar(pregunta):
    abierta = st.session_state.get("faq_abierta")
    st.session_state["faq_abierta"] = None if abierta == pregunta else pregunta


def _tarjeta(duda, doc):
    with st.container(border=True, key="fc-tarjeta-faq"):
        st.html('<p class="fc-antetitulo">Respuesta</p>')
        for parte in duda["respuesta"]:
            st.markdown(parte["frase"])
            mostrar_citas([parte["cita_verificada"]], doc)
        st.caption("Redactada con ayuda de IA y revisada por una persona del equipo. No se genera en el momento.")


def render(doc):
    dudas = publicables(doc)
    if not dudas:
        return
    st.html('<p class="fc-antetitulo">Dudas comunes</p>')
    st.caption("Las eligió el equipo. No salen de lo que escriben las personas, porque no lo guardamos.")
    for i, duda in enumerate(dudas):
        abierta = st.session_state.get("faq_abierta") == duda["pregunta"]
        st.button(duda["pregunta"], key=f"fc-faq-{i}", width="stretch", on_click=_alternar, args=(duda["pregunta"],),
                  icon=":material/expand_less:" if abierta else ":material/expand_more:")
        if abierta:
            _tarjeta(duda, doc)
