"""Módulo 3 · Pregúntale al Estado: prepara un borrador de solicitud. La persona decide si lo envía.

Los datos jurídicos (ley, plazos, pasos, portal) se leen desde config/transparencia.yaml, nunca del modelo.
"""
from html import escape
from pathlib import Path

import streamlit as st
import yaml

from core import filtro, guardrail, prompts
from core.citas import verificar
from core.documento import para_prompt
from core.llm import complete
from modulos.comun import aviso_otro_tema, encabezado, ejecutar, mostrar_citas, valorar

CONFIG = Path(__file__).resolve().parents[1] / "config" / "transparencia.yaml"
POR_VERIFICAR = '<span class="fc-pill fc-pill--aviso">Por verificar</span>'


def cargar_config():
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def preparar_solicitud(duda, doc):
    """La IA sugiere organismo y redacta lo que se pide; la app arma el borrador con la plantilla."""
    categoria = filtro.clasificar(duda, doc)
    if categoria in (filtro.OPINION, filtro.OTRO_TEMA):
        return {"categoria": categoria}
    datos = complete(prompts.TRANSPARENCIA, f"{para_prompt(doc)}\n\nDUDA DE LA PERSONA:\n{guardrail.delimitar(duda)}")
    cfg = cargar_config()
    organismo = str(datos.get("organismo", "")).strip() or "[ORGANISMO]"
    borrador = cfg["plantilla"]["texto"].format(
        organismo=organismo, ley=cfg["ley"]["texto"], solicitud=str(datos.get("respuesta", "")).strip())
    return {"categoria": categoria, "organismo": organismo, "borrador": borrador,
            "justificacion": str(datos.get("justificacion", "")).strip(),
            "citas": verificar(datos.get("citas"), doc)}


def _dato(item):
    return escape(item["texto"]) + (f" {POR_VERIFICAR}" if item.get("estado") == "VERIFICAR" else "")


def render(doc):
    cfg = cargar_config()
    encabezado("Paso 3 · Preguntar", "Pregúntale al Estado",
               "Si el documento no responde tu duda, te ayudamos a preparar una solicitud de acceso a la información pública.")
    with st.container(border=True, key="fc-tarjeta-duda"):
        ejemplo = (doc.get("ejemplos") or {}).get("duda", "¿Cuántas personas se verán beneficiadas?")
        duda = st.text_area("Tu duda", key="duda_estado", max_chars=500, placeholder=f"Ej: {ejemplo}")
        st.caption("No escribas tu nombre ni otros datos personales aquí.")
        if st.button("Preparar borrador", type="primary", icon=":material/edit_note:", width="stretch") and duda.strip():
            st.session_state["est"] = ejecutar(preparar_solicitud, duda.strip(), doc, previo=st.session_state.get("est"))

    r = st.session_state.get("est")
    if not r:
        return
    if r["categoria"] == filtro.OPINION:
        st.info(filtro.MENSAJE_FIJO, title="Fuente Clara no opina", icon=":material/balance:")
        valorar(r, "Pregúntale al Estado")
        return
    if r["categoria"] == filtro.OTRO_TEMA:
        aviso_otro_tema(doc)  # el documento no trata el asunto: no se prepara borrador
        valorar(r, "Pregúntale al Estado")
        return
    if r["categoria"] == filtro.DENTRO:
        st.info("Puede que el documento ya responda esto. Prueba también en «Explícame».", icon=":material/menu_book:")

    with st.container(border=True, key="fc-tarjeta-solicitud"):
        st.html(f'<p class="fc-antetitulo">Organismo sugerido</p><h3 class="fc-h3">{escape(r["organismo"])}</h3>'
                f'<p class="fc-texto-2">{escape(r["justificacion"])}</p>'
                f'<div class="fc-pills"><span class="fc-pill">Sugerencia de la IA · confírmalo en el portal</span></div>')
        if r["citas"]:
            mostrar_citas(r["citas"], doc)
        aviso = f" {POR_VERIFICAR}" if cfg["plantilla"].get("estado") == "VERIFICAR" else ""
        st.html(f'<p class="fc-antetitulo">Borrador de solicitud{aviso}</p>')
        st.code(r["borrador"], language=None, wrap_lines=True)

    # Punto de decisión humana: el enlace al portal solo aparece cuando la persona confirma.
    with st.container(border=True, key="fc-decision"):
        st.html('<p class="fc-antetitulo">Tú decides</p>'
                '<h3 class="fc-h3">Revisa el borrador. Tú decides si lo envías en el Portal de Transparencia.</h3>'
                '<p class="fc-texto-2">Fuente Clara no envía nada y no guarda tu duda, salvo que tú lo autorices '
                'al votar la respuesta. Tu nombre y dirección los '
                'completas directamente en el portal oficial.</p>'
                '<p class="fc-antetitulo" style="margin-top:1rem">Pasos</p>'
                f'<ol class="fc-pasos">{"".join(f"<li>{_dato(p)}</li>" for p in cfg["pasos"])}</ol>'
                '<p class="fc-antetitulo" style="margin-top:.5rem">Plazos</p>'
                f'<ul class="fc-pasos">{"".join(f"<li>{_dato(p)}</li>" for p in cfg["plazos"])}</ul>'
                f'<p class="fc-legal">Base legal: <a href="{escape(cfg["ley"]["url"])}" target="_blank" rel="noopener">'
                f'{escape(cfg["ley"]["texto"])}</a>{" " + POR_VERIFICAR if cfg["ley"].get("estado") == "VERIFICAR" else ""}</p>')
        if st.checkbox("Revisé el borrador y entiendo que yo decido si enviarlo."):
            st.link_button(f"Ir al {cfg['portal']['texto']}", cfg["portal"]["url"], type="primary",
                           icon=":material/open_in_new:", width="stretch")
    valorar(r, "Pregúntale al Estado")
