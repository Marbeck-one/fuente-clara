"""Módulo 2 · Verifica esto: pone lado a lado una afirmación y el texto oficial. No da veredictos."""
from html import escape

import streamlit as st

from core import filtro, prompts
from core.citas import hay_verificada, verificar
from core.documento import para_prompt
from core.llm import complete
from modulos.comun import encabezado, ejecutar, mostrar_citas

# Etiquetas descriptivas fijadas por la app (la IA solo elige la clave).
# Las tres comparten el mismo color: el color nunca da veredicto (DESIGN.md §4).
ETIQUETAS = {
    "respalda": "＝ El texto lo respalda",
    "dice_otra_cosa": "≠ El texto dice otra cosa",
    "no_menciona": "∅ El texto no lo menciona",
}


def comparar(texto, doc):
    """Pasa por el filtro y compara cada afirmación con el documento, verificando las citas."""
    categoria = filtro.clasificar(texto, doc, tipo="afirmación")
    if categoria == filtro.OPINION:
        return {"categoria": categoria}
    datos = complete(prompts.VERIFICA, f"{para_prompt(doc)}\n\nAFIRMACIÓN A COMPARAR:\n{texto}")
    comparaciones = []
    for c in datos.get("comparaciones") or []:
        if isinstance(c, dict):
            comparaciones.append({
                "afirmacion": str(c.get("afirmacion", "")),
                "texto_oficial": str(c.get("texto_oficial", "")),
                "etiqueta": c.get("etiqueta") if c.get("etiqueta") in ETIQUETAS else None,
                "citas": verificar(c.get("citas"), doc),
            })
    return {"categoria": categoria, "comparaciones": comparaciones}


def _tarjeta(c):
    # Sin cita verificada, solo "no lo menciona" se puede mostrar como válido.
    valida = c["etiqueta"] == "no_menciona" or (c["etiqueta"] and hay_verificada(c["citas"]))
    oficial = (f"<p>{escape(c['texto_oficial'])}</p>" if valida
               else '<p class="fc-lado--vacio">Sin cita verificada: no mostramos esta comparación.</p>')
    st.html(f'<div class="fc-comparacion">'
            f'<div class="fc-lado fc-lado--afirmacion"><p class="fc-antetitulo">Lo que dice la afirmación</p>'
            f'<p>{escape(c["afirmacion"])}</p></div>'
            f'<div class="fc-lado fc-lado--oficial"><p class="fc-antetitulo">Lo que dice el texto oficial</p>{oficial}</div>'
            f'</div>')
    if valida:
        st.html(f'<span class="fc-pill fc-pill--etiqueta">{ETIQUETAS[c["etiqueta"]]}</span>')
    else:
        st.warning("No pudimos respaldar esta comparación con una cita del documento. No la tomes como válida.",
                   icon=":material/report:")


def render(doc):
    encabezado("Paso 2 · Verificar", "Verifica esto",
               "Pega una cadena, post o titular. Lo ponemos al lado de lo que dice el texto oficial.")
    with st.form("form_verifica"):
        ejemplo = (doc.get("ejemplos") or {}).get("afirmacion", "«Con esta ley ya no se podrá…»")
        texto = st.text_area("Texto a comparar", max_chars=1500, placeholder=f"Ej: {ejemplo}")
        enviar = st.form_submit_button("Comparar con el texto oficial", type="primary",
                                       icon=":material/compare_arrows:", width="stretch")
    if enviar and texto.strip():
        st.session_state["ver"] = ejecutar(comparar, texto.strip(), doc)

    r = st.session_state.get("ver")
    if not r:
        return
    if r["categoria"] == filtro.OPINION:
        st.info(filtro.MENSAJE_FIJO, title="Fuente Clara no opina", icon=":material/balance:")
        return
    if not r["comparaciones"]:
        st.warning("No encontramos afirmaciones sobre el contenido del documento para comparar.", icon=":material/report:")
    for i, c in enumerate(r["comparaciones"]):
        with st.container(border=True, key=f"fc-tarjeta-comparacion-{i}"):
            _tarjeta(c)
            mostrar_citas(c["citas"], doc)
    st.caption("Fuente Clara no dice quién tiene razón: muestra el texto oficial para que tú compares y decidas.")
