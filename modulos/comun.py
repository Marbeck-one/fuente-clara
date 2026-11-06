"""Piezas de interfaz compartidas. Estilos en static/estilo.css; criterios en DESIGN.md."""
import uuid
from html import escape
from pathlib import Path

import streamlit as st

from core import filtro, votos
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
    """Llama a la IA con un indicador de espera. Si falla, avisa y devuelve None.

    El primer argumento de `funcion` es siempre el texto de la persona. Al resultado se le agrega
    lo necesario para votarlo: un id, ese texto (queda solo en la sesión) y con qué se generó.
    """
    try:
        with st.spinner("Leyendo el documento…"):
            r = filtro.revisar_respuesta(funcion(*args))  # guardrail, capa 3
    except ErrorLLM as e:
        st.error(f"Revisa tu archivo .env o intenta de nuevo. ({e})",
                 title="No pudimos obtener respuesta", icon=":material/cloud_off:")
        return None
    r.update(id=uuid.uuid4().hex[:12], entrada=args[0], documento=st.session_state.get("doc_actual"),
             traza=votos.traza())
    return r


def _al_votar(r, pestana):
    valor = st.session_state.get(f"fc-pulgar-{r['id']}")
    if valor is None:
        return
    try:
        votos.votar(r, pestana, bueno=valor == 1)
    except OSError:
        st.toast("No pudimos guardar tu voto.", icon=":material/error:")
        return
    st.session_state.setdefault("votos", {})[r["id"]] = "bueno" if valor == 1 else "malo"


def _al_detallar(r):
    rid = r["id"]
    try:
        votos.detallar(r, st.session_state.get(f"fc-motivo-{rid}"), st.session_state.get(f"fc-autoriza-{rid}"))
    except OSError:
        st.toast("No pudimos guardar tu comentario.", icon=":material/error:")
    st.session_state["votos"][rid] = "listo"


def valorar(r, pestana):
    """Voto 👍/👎 bajo cada respuesta. Con 👎 pide el motivo y, solo si la persona autoriza, guarda el texto."""
    rid, estado = r["id"], st.session_state.get("votos", {}).get(r["id"])
    with st.container(key=f"fc-voto-{rid}"):
        if estado is None:
            st.caption("¿Te sirvió esta respuesta?")
            st.feedback("thumbs", key=f"fc-pulgar-{rid}", on_change=_al_votar, args=(r, pestana))
        elif estado == "malo":
            with st.form(f"fc-detalle-{rid}", border=False):
                st.pills("¿Qué falló?", votos.MOTIVOS, key=f"fc-motivo-{rid}")
                st.checkbox("Guardar mi pregunta y esta respuesta para mejorar las respuestas del modelo. "
                            "Solo el equipo de Fuente Clara podrá leerlas.", key=f"fc-autoriza-{rid}")
                st.caption("Si escribiste datos personales, no lo marques. Igual ocultamos RUT, correos y teléfonos.")
                st.form_submit_button("Enviar", on_click=_al_detallar, args=(r,))
        else:
            st.caption("Gracias. Tu voto nos ayuda a medir la calidad de las respuestas.")
        st.caption(f"Respuesta generada con {r['traza']['modelo']} · instrucciones {r['traza']['version']}")


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
