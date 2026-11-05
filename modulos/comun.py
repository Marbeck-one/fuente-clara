"""Piezas de interfaz compartidas. Estilos en static/estilo.css; criterios en DESIGN.md."""
from html import escape
from pathlib import Path

import streamlit as st

from core.llm import ErrorLLM

STATIC = Path(__file__).resolve().parents[1] / "static"
PESTANAS = [":material/menu_book: Explícame", ":material/compare_arrows: Verifica esto",
            ":material/account_balance: Pregúntale al Estado"]


def estilos():
    # st.html sanea las etiquetas <style>; st.markdown las respeta.
    st.markdown(f"<style>{(STATIC / 'estilo.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def logo(px=32):
    return f'<img src="app/static/logo.svg" width="{px}" height="{px}" alt="">'


def encabezado(antetitulo, titulo, bajada):
    st.html(f'<div class="fc-seccion"><p class="fc-antetitulo">{escape(antetitulo)}</p>'
            f'<h2>{escape(titulo)}</h2><p class="fc-bajada">{escape(bajada)}</p></div>')


def ejecutar(funcion, *args):
    """Llama a la IA con un indicador de espera. Si falla, avisa y devuelve None."""
    try:
        with st.spinner("Leyendo el documento…"):
            return funcion(*args)
    except ErrorLLM as e:
        st.error(f"Revisa tu archivo .env o intenta de nuevo. ({e})",
                 title="No pudimos obtener respuesta", icon=":material/cloud_off:")
        return None


def enlace_fuente(doc):
    if doc.get("fuente_url"):
        return (f'Fuente oficial: <a href="{escape(doc["fuente_url"])}" target="_blank" rel="noopener">'
                f'{escape(doc["fuente_nombre"])}</a>')
    return f"Fuente: {escape(doc['fuente_nombre'])}"


def mostrar_citas(citas, doc):
    """Cada cita en un expander. El texto literal va en serif y resaltado: es la voz del documento."""
    abrir = True  # se abre solo la primera cita verificada
    for c in citas:
        ok = c["verificada"]
        estado = "Cita verificada" if ok else "Cita no encontrada en el documento"
        with st.expander(f"{c['articulo']} · página {c['pagina']} · {estado}", expanded=ok and abrir,
                         icon=":material/verified:" if ok else ":material/report:"):
            texto = f"<mark>{escape(c['texto_literal'])}</mark>" if ok else escape(c["texto_literal"])
            nota = enlace_fuente(doc) if ok else "Este texto no aparece en el documento. No lo tomes como cita."
            st.html(f'<blockquote class="fc-cita{"" if ok else " fc-cita--no"}">«{texto}»</blockquote>'
                    f'<p class="fc-cita-meta">{nota}</p>')
        abrir = abrir and not ok
