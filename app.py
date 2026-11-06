"""Fuente Clara: entender, verificar y preguntar sobre un documento público oficial.

Ejecutar con:  streamlit run app.py
La cuenta es opcional y por defecto está desactivada (ver modulos/cuenta.py). Lo que escribe la persona vive
solo en st.session_state; se guarda únicamente si ella lo autoriza al votar una respuesta (ver core/votos.py).
"""
from html import escape

import streamlit as st

from core import documento
from core.llm import ErrorLLM, configuracion
from modulos import accesibilidad, cuenta, explicame, panel, transparencia, verifica
from modulos.comun import PESTANAS, STATIC, enlace_fuente, estilos, logo

st.set_page_config(page_title="Fuente Clara", page_icon=str(STATIC / "favicon.svg"), layout="centered")
estilos()


@st.cache_data(show_spinner=False)
def cargar_documento(archivo):
    return documento.cargar(archivo)


def inicio():
    catalogo = documento.listar()
    if not catalogo:
        st.error("No hay documentos registrados en data/documentos/catalogo.yaml.")
        st.stop()
    titulos = {d["titulo"]: d["archivo"] for d in catalogo}
    elegido = st.selectbox("Documento", list(titulos)) if len(titulos) > 1 else next(iter(titulos))
    archivo = titulos[elegido]
    if st.session_state.get("doc_actual") != archivo:  # al cambiar de documento se borran los resultados
        for clave in ("exp", "ver", "est", "faq_abierta", "ver_texto", "ver_recortado", "ver_archivo",
                      "ver_camara", "ver_camara_activa"):
            st.session_state.pop(clave, None)
        st.session_state["doc_actual"] = archivo
    doc = cargar_documento(archivo)

    # El documento es el protagonista: nombre y fuente oficial siempre arriba.
    pills = ['<span class="fc-pill fc-pill--aviso">Ejemplo ficticio · no es un documento oficial</span>'] if doc.get("ficticio") else []
    try:
        proveedor, modelo = configuracion()
        pills.append(f'<span class="fc-pill" title="Detalle en DECLARACION_IA.md">IA: {escape(modelo)}</span>')
    except ErrorLLM as e:
        st.error(str(e))
    st.html(f'<section class="fc-doc"><p class="fc-antetitulo">Estás leyendo</p><h1>{escape(doc["titulo"])}</h1>'
            f'<p class="fc-fuente">{enlace_fuente(doc)}</p><div class="fc-pills">{"".join(pills)}</div></section>')

    st.info("**Esta herramienta usa inteligencia artificial.** Puede equivocarse. No reemplaza tu criterio: "
            "revisa siempre el texto oficial y decide tú.",
            icon=":material/smart_toy:")

    tab1, tab2, tab3 = st.tabs(PESTANAS, key="pestana", on_change="rerun")
    with tab1:
        explicame.render(doc)
    with tab2:
        verifica.render(doc)
    with tab3:
        transparencia.render(doc)


PAGINA_INICIO = st.Page(inicio, title="Fuente Clara", default=True)
PAGINA_CALIDAD = st.Page(panel.render, title="Calidad de las respuestas · Fuente Clara", url_path="calidad")

st.html(f'<header class="fc-marca">{logo()}<div><p class="fc-logotipo"><b>Fuente</b><span>Clara</span></p>'
        '<p class="fc-lema">Lo que dice el documento, dicho claro.</p></div></header>')
accesibilidad.render_interruptor()
cuenta.render()
pagina = st.navigation([PAGINA_INICIO, PAGINA_CALIDAD], position="hidden")
pagina.run()
if pagina.url_path == PAGINA_CALIDAD.url_path:
    st.page_link(PAGINA_INICIO, label="Volver a Fuente Clara", icon=":material/arrow_back:")
else:
    st.page_link(PAGINA_CALIDAD, label="Cómo nos va: calidad de las respuestas", icon=":material/insights:")

st.html(f'<footer class="fc-pie">{logo(16)}<span>Esta herramienta solo explica el documento cargado. '
        'No opina ni recomienda.</span></footer>')
