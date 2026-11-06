"""Módulo 1 · Explícame: explica el documento en lenguaje claro, con citas verificadas."""
from html import escape

import streamlit as st

from core import filtro, guardrail, prompts
from core.citas import verificar
from core.documento import para_prompt
from core.llm import complete
from modulos import voz
from modulos.comun import PESTANAS, aviso_otro_tema, encabezado, ejecutar, enlace_fuente, valorar

PERFILES = ["Estudiante", "Trabajador/a", "Adulto mayor"]  # por defecto; cada documento puede definir los suyos
ICONOS = {"Estudiante": ":material/school:", "Trabajador/a": ":material/work:", "Adulto mayor": ":material/elderly:",
          "Apoderado/a": ":material/family_restroom:", "Docente": ":material/co_present:"}


def perfiles(doc):
    return doc.get("perfiles") or PERFILES


def _frases(items, doc):
    """Solo las frases con al menos una cita verificada. Las demás no se muestran.

    Devuelve (frases a mostrar, cantidad descartada, todas las citas revisadas).
    """
    mostrar, descartadas, revisadas = [], 0, []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            descartadas += 1
            continue
        citas = verificar(item.get("citas") or [], doc)
        revisadas += citas
        validas = [c for c in citas if c["verificada"]]
        texto = str(item.get("texto", "")).strip()
        if texto and validas:
            mostrar.append({"texto": texto, "citas": validas})
        else:
            descartadas += 1
    return mostrar, descartadas, revisadas


def explicar(pregunta, perfil, doc):
    """Pasa por el filtro y, si corresponde, pide la explicación y verifica cada frase con sus citas."""
    categoria = filtro.clasificar(pregunta, doc)
    if categoria != filtro.DENTRO:
        return {"categoria": categoria}  # FUERA, OTRO_TEMA u OPINION: no se llama al modelo de respuesta
    perfil_txt = perfil if perfil in perfiles(doc) else "ninguno"
    datos = complete(prompts.EXPLICAME, f"{para_prompt(doc)}\n\nPERFIL: {perfil_txt}\nPREGUNTA:\n{guardrail.delimitar(pregunta)}")
    en_documento = str(datos.get("en_documento")).lower() == "true"
    frases, sin_cita, revisadas = _frases(datos.get("frases"), doc)
    que_cambia, _, revisadas_perfil = _frases(datos.get("que_cambia_para_ti"), doc)
    return {"categoria": filtro.DENTRO if en_documento else filtro.FUERA, "perfil": perfil_txt,
            "respuesta": " ".join(f["texto"] for f in frases),
            "que_cambia": " ".join(f["texto"] for f in que_cambia),
            "frases": frases, "que_cambia_frases": que_cambia,
            "frases_total": len(frases) + sin_cita,
            "frases_sin_cita": sin_cita,
            "citas": revisadas + revisadas_perfil}


def _pasar_a_estado(duda):
    st.session_state["duda_estado"] = duda
    st.session_state["pestana"] = PESTANAS[2]  # abre la pestaña 3 con la duda ya escrita


def _frase(f):
    """Lenguaje claro a la izquierda; el texto literal del documento, con su artículo y página, a la derecha."""
    literales = "".join(f'<p><mark>{escape(c["texto_literal"])}</mark></p>' for c in f["citas"])
    articulo = f["citas"][0]
    st.html(f'<div class="fc-comparacion">'
            f'<div class="fc-lado fc-lado--afirmacion"><p class="fc-antetitulo">En palabras simples</p>'
            f'<p>{escape(f["texto"])}</p></div>'
            f'<div class="fc-lado fc-lado--oficial"><p class="fc-antetitulo">Lo que dice el texto · '
            f'{escape(str(articulo["articulo"]))}, página {articulo["pagina"]}</p>{literales}</div>'
            f'</div>')


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
    elif not r["frases"]:
        st.warning("No encontramos en el documento el texto que respalda esta respuesta, así que no la mostramos. "
                   "Intenta preguntar de otra manera.", title="No pudimos comprobar esta respuesta", icon=":material/report:")
    else:
        with st.container(border=True, key="fc-tarjeta-respuesta"):
            st.html('<p class="fc-antetitulo">Respuesta</p>')
            voz.boton_escuchar(voz.texto_explicame(r), key="explicame")
            for f in r["frases"]:
                _frase(f)
            if r["perfil"] != "ninguno":
                with st.container(key="fc-para-ti"):
                    st.html(f'<p class="fc-antetitulo">Qué cambia para ti · {escape(r["perfil"])}</p>')
                    if r["que_cambia_frases"]:
                        for f in r["que_cambia_frases"]:
                            _frase(f)
                    else:
                        st.caption("El documento no establece nada específico para este perfil.")
            st.html(enlace_fuente(doc))
            st.caption("Solo mostramos frases con su cita del texto oficial. Fuente Clara no dice si son buenas o malas: decides tú.")
    valorar(r, "Explícame")
