"""Panel «Calidad de las respuestas»: cómo evalúan las personas las respuestas de Fuente Clara.

Los números son públicos. Las preguntas y respuestas guardadas (solo con permiso de la persona)
las ve el equipo ingresando la CLAVE_EQUIPO definida en el archivo .env.
"""
import hmac
import os
import sqlite3
import sys
import time
from html import escape

import altair as alt
import pandas as pd
import streamlit as st

from core import cuentas, documento, filtro, votos, jueza
from modulos import cuenta
from modulos.comun import encabezado

# Una sola serie por gráfico: un solo color para todas las barras. Es la familia de «acción»,
# un paso más saturado para que la barra no se lea gris (validado con la guía de visualización).
BARRA = "#0891B2"
TEXTO, TEXTO_2 = "#0F172A", "#475569"
POCOS_VOTOS = 5
MAX_INTENTOS = 5  # intentos de clave por sesión
ORDEN_PESTANAS = ["Explícame", "Verifica esto", "Pregúntale al Estado"]


def _etiqueta(n, buenos):
    return f"{100 * buenos / n:.0f}% · {n} voto{'s' if n != 1 else ''}"


def _agrupar(df, campo, orden):
    """% de votos 👍 por grupo. orden: lista fija, o "valor" para ordenar de mayor a menor."""
    g = df.groupby(campo, sort=False).agg(votos=("bueno", "size"), buenos=("bueno", "sum")).reset_index()
    g["les_sirvio"] = (100 * g["buenos"] / g["votos"]).round()
    g["resultado"] = [_etiqueta(n, b) for n, b in zip(g["votos"], g["buenos"])]
    if orden == "valor":
        return g.sort_values(["les_sirvio", "votos"], ascending=False)
    presentes = set(g[campo])
    return g.set_index(campo).loc[[o for o in orden if o in presentes]].reset_index()


def _barras(tabla, campo, valor, maximo, descripcion):
    """Barras horizontales finas con el resultado escrito en la punta (el eje x sobra: el valor ya está escrito)."""
    base = alt.Chart(tabla).encode(
        y=alt.Y(f"{campo}:N", sort=None, title=None,
                axis=alt.Axis(labelLimit=170, labelFontSize=14, labelColor=TEXTO, labelPadding=8,
                              domain=False, ticks=False)),
        x=alt.X(f"{valor}:Q", title=None, axis=None, scale=alt.Scale(domain=[0, maximo * 2])),
        tooltip=[alt.Tooltip(f"{campo}:N", title="Grupo"), alt.Tooltip("resultado:N", title="Resultado")])
    barras = base.mark_bar(size=18, cornerRadiusEnd=4, color=BARRA)
    texto = base.mark_text(align="left", dx=6, fontSize=13, color=TEXTO_2).encode(text="resultado:N")
    grafico = (barras + texto).properties(height=36 * len(tabla) + 8).configure_view(stroke=None)
    st.altair_chart(grafico, width="stretch", alt=descripcion)


def _publico(df):
    df = df.assign(bueno=df["voto"] == "bueno", instrucciones=df["version"] + " · " + df["modelo"],
                   perfil=df["perfil"].replace({"ninguno": "Sin perfil"}))
    usaron_doc = df[df["categoria"] == filtro.DENTRO]
    c1, c2, c3 = st.columns(3)
    c1.metric("Votos", len(df))
    c2.metric("Les sirvió", f"{100 * df['bueno'].mean():.0f}%")
    c3.metric("Con cita verificada",
              f"{100 * (usaron_doc['citas_verificadas'] > 0).mean():.0f}%" if len(usaron_doc) else "—",
              help="De las respuestas que se basaron en el documento.")

    pestanas = _agrupar(df, "pestana", ORDEN_PESTANAS)
    orden_versiones = df.sort_values("fecha").drop_duplicates("instrucciones")["instrucciones"].tolist()
    versiones = _agrupar(df, "instrucciones", orden_versiones)
    perfiles = _agrupar(df, "perfil", "valor")
    malos = df[~df["bueno"]]
    motivos = (malos["motivo"] if "motivo" in malos else pd.Series(index=malos.index, dtype=object))
    motivos = motivos.fillna("Sin motivo").value_counts().rename_axis("motivo").reset_index(name="votos")
    motivos["resultado"] = motivos["votos"].astype(str)

    st.caption(f"Un porcentaje con menos de {POCOS_VOTOS} votos todavía no es confiable.")
    st.subheader("Les sirvió, por pestaña")
    _barras(pestanas, "pestana", "les_sirvio", 100, "Porcentaje de votos positivos en cada pestaña.")
    st.subheader("Les sirvió, por versión de las instrucciones")
    st.caption("De la más antigua a la más nueva. Si una versión nueva baja, ese cambio empeoró las respuestas.")
    _barras(versiones, "instrucciones", "les_sirvio", 100, "Porcentaje de votos positivos por versión de instrucciones.")
    st.subheader("Les sirvió, por perfil")
    _barras(perfiles, "perfil", "les_sirvio", 100, "Porcentaje de votos positivos por perfil.")
    st.subheader("Por qué no les sirvió")
    if motivos.empty:
        st.caption("Nadie ha marcado 👎 todavía.")
    else:
        _barras(motivos, "motivo", "votos", motivos["votos"].max(), "Cantidad de votos negativos por motivo.")

    with st.expander("Ver los datos como tabla", icon=":material/table:"):
        for titulo, tabla, campo in (("Por pestaña", pestanas, "pestana"), ("Por versión", versiones, "instrucciones"),
                                     ("Por perfil", perfiles, "perfil")):
            st.caption(titulo)
            st.dataframe(tabla[[campo, "votos", "buenos", "les_sirvio"]].rename(
                columns={campo: "Grupo", "votos": "Votos", "buenos": "👍", "les_sirvio": "Les sirvió (%)"}),
                hide_index=True, width="stretch")
        st.caption("Motivos de 👎")
        st.dataframe(motivos[["motivo", "votos"]].rename(columns={"motivo": "Motivo", "votos": "Votos"}),
                     hide_index=True, width="stretch")


def _uso():
    """Cuántas personas usan la cuenta y cuánto se consulta. Son conteos: no identifican a nadie."""
    try:
        datos = cuentas.resumen()
    except sqlite3.Error as e:
        print(f"[Fuente Clara] No se pudo leer el uso: {e}", file=sys.stderr)
        st.caption("No pudimos leer los datos de uso.")
        return
    st.subheader("Uso de Fuente Clara")
    if cuentas.es_mock():
        st.caption("Modo demostración: estos datos vienen de un usuario simulado, no de personas reales.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cuentas", datos["cuentas"])
    c2.metric("Activas en 7 días", datos["activas"])
    c3.metric("Volvieron otro día", datos["volvieron"])
    c1, c2 = st.columns(2)
    c1.metric("Consultas con cuenta", datos["con_cuenta"])
    c2.metric("Consultas sin cuenta", datos["sin_cuenta"])
    if datos["por_modulo"]:
        tabla = pd.DataFrame([{"modulo": m, "consultas": n, "resultado": str(n)}
                              for m, n in datos["por_modulo"].items()])
        tabla = tabla.sort_values("consultas", ascending=False)
        st.caption("Consultas por módulo")
        _barras(tabla, "modulo", "consultas", tabla["consultas"].max(), "Cantidad de consultas en cada módulo.")


def _verificar_clave():
    """Se revisa una sola vez por clave escrita (no en cada recarga), con 1 segundo de espera si falla."""
    ingresada = st.session_state.get("fc-clave", "")
    if not ingresada:
        return
    if hmac.compare_digest(ingresada.encode(), os.getenv("CLAVE_EQUIPO", "").encode()):
        st.session_state["fc-equipo-ok"] = True
    else:
        st.session_state["fc-intentos-clave"] = st.session_state.get("fc-intentos-clave", 0) + 1
        time.sleep(1)
    st.session_state["fc-clave"] = ""


def _privado(registros, titulos):
    st.subheader("Respuestas a revisar")
    st.caption("Las que alguien votó 👎 y autorizó guardar para mejorar las respuestas del modelo. Solo para el equipo.")
    if not os.getenv("CLAVE_EQUIPO", ""):
        st.caption("Para ver esta sección, define CLAVE_EQUIPO en el archivo .env.")
        return
    if not st.session_state.get("fc-equipo-ok"):
        intentos = st.session_state.get("fc-intentos-clave", 0)
        if intentos >= MAX_INTENTOS:
            st.error("Demasiados intentos fallidos. Vuelve a intentarlo más tarde.", icon=":material/lock:")
            return
        st.text_input("Clave del equipo", type="password", key="fc-clave", on_change=_verificar_clave)
        if intentos:
            st.error(f"Clave incorrecta. Te quedan {MAX_INTENTOS - intentos} intentos.")
        return
    guardadas = sorted((v for v in registros if v.get("autoriza")), key=lambda v: v["fecha"], reverse=True)
    if not guardadas:
        st.info("Todavía no hay respuestas guardadas.", icon=":material/inbox:")
    for v in guardadas:
        with st.expander(f"{v['fecha'][:16].replace('T', ' ')} · {v['pestana']} · {v.get('motivo') or 'Sin motivo'}"):
            citas = "".join(
                f'<li>{"Verificada" if c["verificada"] else "No encontrada"} · {escape(str(c["articulo"]))}, '
                f'página {escape(str(c["pagina"]))}: «{escape(c["texto_literal"])}»</li>' for c in v.get("citas") or [])
            st.html(f'<p class="fc-antetitulo">Pregunta</p><p style="white-space:pre-wrap">{escape(v["pregunta"])}</p>'
                    f'<p class="fc-antetitulo">Respuesta</p><p style="white-space:pre-wrap">{escape(v["respuesta"])}</p>'
                    + (f'<p class="fc-antetitulo">Citas</p><ul>{citas}</ul>' if citas else "")
                    + f'<p class="fc-texto-2">{escape(v["modelo"])} · instrucciones {escape(v["version"])} · '
                      f'perfil {escape(v["perfil"])} · {escape(titulos.get(v.get("documento"), str(v.get("documento"))))}</p>')


def _jueza():
    """Respuestas que la segunda revisión con IA (issue #29) no dejó mostrar. Solo motivo y modelo: nunca el texto."""
    bloqueos = jueza.leer()
    if not (bloqueos or jueza.activa()):
        return
    st.subheader("Segunda revisión con IA")
    st.caption("Otra IA lee cada respuesta antes de mostrarla y la bloquea si opina, recomienda, toma partido o afirma algo "
               "que las citas no respaldan." + ("" if jueza.activa() else " Ahora está apagada (LLM_JUEZA en .env)."))
    st.metric("Respuestas bloqueadas antes de mostrarse", len(bloqueos))
    if bloqueos:
        conteo = pd.DataFrame(bloqueos)["motivo"].map(lambda m: jueza.MOTIVOS.get(m, m)).value_counts()
        st.dataframe(conteo.rename_axis("Motivo").reset_index(name="Respuestas"), hide_index=True, width="stretch")


def render():
    encabezado("Transparencia", "Calidad de las respuestas",
               "Así evalúan las personas las respuestas de Fuente Clara. Sirve para saber si un cambio en el "
               "modelo o en sus instrucciones las mejoró o las empeoró.")
    registros = votos.leer()
    titulos = {d["archivo"]: d["titulo"] for d in documento.listar()}
    presentes = sorted({v.get("documento") for v in registros}, key=str)
    if len(presentes) > 1:
        elegido = st.selectbox("Documento", ["Todos"] + presentes,
                               format_func=lambda a: a if a == "Todos" else titulos.get(a, str(a)))
        if elegido != "Todos":
            registros = [v for v in registros if v.get("documento") == elegido]
    if registros:
        _publico(pd.DataFrame(registros))
    else:
        st.info("Todavía no hay votos. Aparecerán aquí cuando las personas evalúen las respuestas.",
                icon=":material/hourglass_empty:")
    _jueza()
    if cuenta.modo():
        _uso()
    _privado(registros, titulos)
