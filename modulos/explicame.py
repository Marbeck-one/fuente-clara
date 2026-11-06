"""Módulo 1 · Explícame: explica el documento en lenguaje claro, con citas verificadas."""
from html import escape

import streamlit as st

from core import filtro, guardrail, prompts
from core.citas import hay_verificada, verificar
from core.documento import para_prompt
from core.llm import complete
from modulos import voz
from modulos.comun import PESTANAS, aviso_otro_tema, encabezado, ejecutar, mostrar_citas, valorar

PERFILES = ["Estudiante", "Trabajador/a", "Adulto mayor"]  # por defecto; cada documento puede definir los suyos
ICONOS = {"Estudiante": ":material/school:", "Trabajador/a": ":material/work:", "Adulto mayor": ":material/elderly:",
          "Apoderado/a": ":material/family_restroom:", "Docente": ":material/co_present:"}


def perfiles(doc):
    return doc.get("perfiles") or PERFILES


def explicar(pregunta, perfil, doc):
    """Pasa por el filtro y, si corresponde, pide la explicación y verifica sus citas."""
    categoria = filtro.clasificar(pregunta, doc)
    if categoria != filtro.DENTRO:
        return {"categoria": categoria}  # FUERA, OTRO_TEMA u OPINION: no se llama al modelo de respuesta
    perfil_txt = perfil if perfil in perfiles(doc) else "ninguno"
    datos = complete(prompts.EXPLICAME, f"{para_prompt(doc)}\n\nPERFIL: {perfil_txt}\nPREGUNTA:\n{guardrail.delimitar(pregunta)}")
    en_documento = str(datos.get("en_documento")).lower() == "true"
    return {"categoria": filtro.DENTRO if en_documento else filtro.FUERA, "perfil": perfil_txt,
            "respuesta": str(datos.get("respuesta", "")),
            "que_cambia": str(datos.get("que_cambia_para_ti", "")).strip(),
            "citas": verificar(datos.get("citas"), doc)}


def _pasar_a_estado(duda):
    st.session_state["duda_estado"] = duda
    st.session_state["pestana"] = PESTANAS[2]  # abre la pestaña 3 con la duda ya escrita


def render(doc):
    encabezado("Paso 1 · Entender", "Explícame", "Pregunta con tus palabras. Te respondemos solo con lo que dice el documento.")
    with st.form("form_explicame"):
        ejemplo = (doc.get("ejemplos") or {}).get("pregunta", "¿A quién se aplica?")
        pregunta = st.text_area("Tu pregunta", max_chars=500, placeholder=f"Ej: {ejemplo}")
        voz.boton_dictar("Tu pregunta")
        perfil = st.pills("¿Quieres saber qué cambia para ti? (opcional)", perfiles(doc),
                          format_func=lambda p: f"{ICONOS.get(p, ':material/person:')} {p}")
        enviar = st.form_submit_button("Explícame", type="primary", icon=":material/auto_stories:", width="stretch")
    if enviar and pregunta.strip():
        st.session_state["exp_pregunta"] = pregunta.strip()
        st.session_state["exp"] = ejecutar(explicar, pregunta.strip(), perfil, doc, previo=st.session_state.get("exp"))

    r = st.session_state.get("exp")
    if not r:
        return
    if r["categoria"] == filtro.OPINION:
        st.info(filtro.MENSAJE_FIJO, title="Fuente Clara no opina", icon=":material/balance:")
    elif r["categoria"] == filtro.OTRO_TEMA:
        aviso_otro_tema(doc)  # sin botón: preguntarle al Estado no sirve para un tema que el documento no trata
    elif r["categoria"] == filtro.FUERA:
        st.info("Preferimos decírtelo antes que adivinar. Puedes preguntarle directamente al organismo que tiene la información.",
                title="El documento no responde esta pregunta", icon=":material/search_off:")
        st.button("Pregúntale al Estado", type="primary", icon=":material/arrow_forward:", icon_position="right",
                  width="stretch", on_click=_pasar_a_estado, args=(st.session_state["exp_pregunta"],))
    elif not hay_verificada(r["citas"]):
        st.warning("No encontramos en el documento el texto que respalda esta respuesta, así que no la mostramos. "
                   "Intenta preguntar de otra manera.", title="No pudimos comprobar esta respuesta", icon=":material/report:")
    else:
        with st.container(border=True, key="fc-tarjeta-respuesta"):
            st.html('<p class="fc-antetitulo">Respuesta</p>')
            voz.boton_escuchar(voz.texto_explicame(r), key="explicame")
            st.markdown(r["respuesta"])
            if r["que_cambia"] and r["perfil"] != "ninguno":
                with st.container(key="fc-para-ti"):
                    st.html(f'<p class="fc-antetitulo">Qué cambia para ti · {escape(r["perfil"])}</p>')
                    st.markdown(r["que_cambia"])
            st.html('<p class="fc-antetitulo">De dónde sale</p>')
            mostrar_citas(r["citas"], doc)
    valorar(r, "Explícame")
