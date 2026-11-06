"""Módulo 2 · Verifica esto: pone lado a lado una afirmación y el texto oficial. No da veredictos."""
import hashlib
import io
import sys
from html import escape

import streamlit as st
from PIL import Image, ImageOps

from core import filtro, guardrail, prompts
from core.citas import hay_verificada, verificar
from core.documento import para_prompt
from core.llm import ErrorLLM, complete
from modulos import voz
from modulos.comun import (aviso_otro_tema, encabezado, ejecutar, mostrar_citas,
                           permitir_consulta, repetido, valorar)

# Etiquetas descriptivas fijadas por la app (la IA solo elige la clave).
# Las tres comparten el mismo color: el color nunca da veredicto (DESIGN.md §4).
ETIQUETAS = {
    "respalda": "＝ El texto lo respalda",
    "dice_otra_cosa": "≠ El texto dice otra cosa",
    "no_menciona": "∅ El texto no lo menciona",
}

MAX_BYTES = 5 * 1024 * 1024
FORMATOS = {"PNG", "JPEG", "WEBP"}


def comparar(texto, doc):
    """Pasa por el filtro y compara cada afirmación con el documento, verificando las citas."""
    categoria = filtro.clasificar(texto, doc, tipo="afirmación")
    if categoria in (filtro.OPINION, filtro.OTRO_TEMA):
        return {"categoria": categoria}
    datos = complete(prompts.VERIFICA, f"{para_prompt(doc)}\n\nAFIRMACIÓN A COMPARAR:\n{guardrail.delimitar(texto)}")
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


def leer_imagen(datos):
    """Valida y normaliza una captura. Lanza ValueError con un mensaje para la persona."""
    if not datos:
        raise ValueError("No recibimos ninguna imagen.")
    if len(datos) > MAX_BYTES:
        raise ValueError("La imagen supera los 5 MB. Recórtala o usa una captura más liviana.")

    try:
        imagen = Image.open(io.BytesIO(datos))
        formato = imagen.format
        imagen.load()
        if formato not in FORMATOS:
            raise ValueError("Formato no compatible. Usa PNG, JPG o WebP.")
        if min(imagen.size) < 60:
            raise ValueError("La imagen es demasiado pequeña para leer texto.")

        # Respeta la orientación del celular y deja la imagen en RGB antes de enviarla.
        imagen = ImageOps.exif_transpose(imagen)
        if imagen.mode != "RGB":
            if imagen.mode in ("RGBA", "LA", "PA") or (
                    imagen.mode == "P" and "transparency" in imagen.info):
                fondo = Image.new("RGB", imagen.size, "white")
                rgba = imagen.convert("RGBA")
                fondo.paste(rgba, mask=rgba.getchannel("A"))
                imagen = fondo
            else:
                imagen = imagen.convert("RGB")
        return imagen
    except ValueError:
        raise
    except Exception:
        raise ValueError("El archivo no es una imagen válida. Usa PNG, JPG o WebP.")


def extraer_texto(imagen):
    """Transcribe literalmente la imagen. La imagen no se guarda."""
    datos = complete(prompts.TRANSCRIBIR, "Transcribe el texto visible en la imagen.", imagen=imagen)
    return str(datos.get("texto", "")).strip()


def _activar_camara():
    st.session_state["ver_camara_activa"] = True


def _cerrar_camara():
    st.session_state["ver_camara_activa"] = False
    st.session_state.pop("ver_camara", None)


def es_valida(c):
    """Sin cita verificada, solo "no lo menciona" se puede mostrar como válido. También lo usa scripts/evaluar.py."""
    return c["etiqueta"] == "no_menciona" or bool(c["etiqueta"] and hay_verificada(c["citas"]))


def _tarjeta(c):
    valida = es_valida(c)
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
    st.session_state.setdefault("ver_texto", "")

    st.info(
        "**Qué puedes hacer aquí:** comparar una afirmación, cadena, post o titular con el texto oficial del documento.\n\n"
        "- **Escribe o sube:** una afirmación concreta sobre el tema del documento, o una captura nítida "
        "donde se lea el texto (publicación, mensaje, titular).\n"
        "- **No sirve para:** fotos de personas, paisajes o memes sin texto, capturas borrosas, "
        "conversaciones privadas con datos personales, opiniones o temas que el documento no trata.\n"
        "- **Cómo usarla:** extrae o pega el texto, revísalo y corrígelo, y después compáralo. "
        "La app no da veredictos: muestra el texto oficial para que tú decidas.\n\n"
        "Para explicaciones usa **Explícame**; si falta un dato, usa **Pregúntale al Estado**.",
        title="Cómo usar Verifica esto",
        icon=":material/info:",
    )

    st.warning("No subas capturas con nombres, teléfonos, RUT, correos ni otros datos personales. "
               "Si aparecen, recórtalos antes de subir la imagen. La captura se envía al proveedor de IA "
               "para transcribirla y no se guarda en Fuente Clara.",
               icon=":material/privacy_tip:")

    with st.container(border=True):
        st.subheader("¿La cadena está en una captura?")
        st.caption("Sube una imagen y la app intentará leer el texto. Revísalo y corrígelo antes de comparar.")
        archivo = st.file_uploader("Captura (PNG, JPG o WebP · máx. 5 MB)",
                                   type=["png", "jpg", "jpeg", "webp"], key="ver_archivo")
        camara = None
        if st.session_state.get("ver_camara_activa"):
            camara = st.camera_input("Toma una foto de la cadena", key="ver_camara")
            st.button("Cerrar cámara", on_click=_cerrar_camara,
                      icon=":material/videocam_off:", key="ver_cerrar_camara")
        else:
            st.button("Activar cámara", on_click=_activar_camara,
                      icon=":material/photo_camera:", key="ver_activar_camara")
        fuente = archivo or camara

        if fuente:
            try:
                imagen = leer_imagen(fuente.getvalue())
            except ValueError as e:
                st.error(str(e), title="No pudimos usar esa imagen", icon=":material/image_not_supported:")
            else:
                st.image(imagen, caption="Vista previa. La imagen no se guarda.", width=420)
                if st.button("Leer texto de la imagen", icon=":material/document_scanner:",
                             width="stretch", key="ver_leer"):
                    firma = "imagen:" + hashlib.sha256(fuente.getvalue()).hexdigest()
                    if repetido(firma):
                        st.toast("Ya leímos esta imagen. Corrige el texto o prueba con otra captura.",
                                 icon=":material/hourglass_top:")
                    elif permitir_consulta():
                        with st.spinner("Leyendo la imagen…"):
                            try:
                                extraido = extraer_texto(imagen)
                            except ErrorLLM as e:
                                print(f"[Fuente Clara] No se pudo leer la imagen: {e}", file=sys.stderr)
                                st.error("No pudimos leer la imagen. Intenta de nuevo o pega el texto a mano.",
                                         title="No pudimos leer la imagen", icon=":material/cloud_off:")
                            else:
                                if not extraido:
                                    st.warning("No encontramos texto legible. Prueba con una captura más nítida "
                                               "o pega el texto a mano.", icon=":material/search_off:")
                                else:
                                    st.session_state["ver_texto"] = extraido[:guardrail.LARGO_MAXIMO]
                                    st.session_state["ver_recortado"] = len(extraido) > guardrail.LARGO_MAXIMO
                                    st.session_state.pop("ver", None)
                                    st.rerun()

    with st.form("form_verifica"):
        ejemplo = (doc.get("ejemplos") or {}).get("afirmacion", "«Con esta ley ya no se podrá…»")
        texto = st.text_area("Texto a comparar", max_chars=guardrail.LARGO_MAXIMO,
                             key="ver_texto", placeholder=f"Ej: {ejemplo}")
        if st.session_state.get("ver_recortado"):
            st.caption("La captura tenía más de 1.500 caracteres. Recortamos el texto; puedes completarlo a mano.")
        enviar = st.form_submit_button("Comparar con el texto oficial", type="primary",
                                       icon=":material/compare_arrows:", width="stretch")
    if enviar:
        if not texto.strip():
            st.warning("Escribe o extrae texto antes de comparar.", icon=":material/edit_note:")
        else:
            st.session_state["ver"] = ejecutar(comparar, texto.strip(), doc, previo=st.session_state.get("ver"))

    r = st.session_state.get("ver")
    if not r:
        return
    if r["categoria"] == filtro.OPINION:
        st.info(filtro.MENSAJE_FIJO, title="Fuente Clara no opina", icon=":material/balance:")
        valorar(r, "Verifica esto")
        return
    if r["categoria"] == filtro.OTRO_TEMA:
        aviso_otro_tema(doc)  # no tiene sentido comparar una afirmación sobre otro asunto
        return
    if not r["comparaciones"]:
        st.warning("No encontramos afirmaciones sobre el contenido del documento para comparar.", icon=":material/report:")
    voz.boton_escuchar(voz.texto_verifica(r, es_valida, ETIQUETAS), key="verifica")
    for i, c in enumerate(r["comparaciones"]):
        with st.container(border=True, key=f"fc-tarjeta-comparacion-{i}"):
            _tarjeta(c)
            mostrar_citas(c["citas"], doc)
    st.caption("Fuente Clara no dice quién tiene razón: muestra el texto oficial para que tú compares y decidas.")
    valorar(r, "Verifica esto")
