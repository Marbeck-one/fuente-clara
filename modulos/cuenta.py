"""Cuenta opcional: entrar, salir, borrar los datos y aplicar el tope que le corresponde a cada persona.

Toda la app pregunta aquí quién es la persona (`actual`), así el modo simulado y el proveedor real solo
se distinguen en este archivo. Sin cuenta se puede usar todo: lo único que cambia es el tope de consultas.
"""
import importlib.util
import os
import sqlite3
import sys

import streamlit as st

from core import cuentas, limites

MOCK, GOOGLE = "mock", "google"
_CLAVE_MOCK = "fc-cuenta-mock"
_CLAVE_REGISTRADA = "fc-cuenta-registrada"
_SECRETO_MOCK = "solo-para-la-demo"  # el usuario simulado no es nadie: no hay identidad que proteger


def _google_configurado():
    """Hacen falta las credenciales ([auth] en secrets.toml), Authlib y el secreto de los seudónimos."""
    if not (os.getenv("CUENTAS_SECRETO") and importlib.util.find_spec("authlib")):
        return False
    try:
        return "auth" in st.secrets
    except Exception:  # sin secrets.toml, Streamlit lanza su propio error; para la app es «no configurado»
        return False


def modo():
    """Cómo se entra: MOCK, GOOGLE o None si el login no está disponible."""
    if cuentas.es_mock():
        return MOCK
    return GOOGLE if _google_configurado() else None


def _registrar(usuario_id, proveedor):
    """Anota el ingreso una vez por sesión. Si falla la base de datos, la persona igual entra."""
    if st.session_state.get(_CLAVE_REGISTRADA) == usuario_id:
        return
    try:
        cuentas.ingresar(usuario_id, proveedor)
    except sqlite3.Error as e:
        print(f"[Fuente Clara] No se pudo registrar el ingreso: {e}", file=sys.stderr)
    st.session_state[_CLAVE_REGISTRADA] = usuario_id


def actual():
    """Identificador seudónimo de quien entró, o None si no hay sesión iniciada."""
    forma = modo()
    if forma == MOCK:
        return st.session_state.get(_CLAVE_MOCK)
    if forma == GOOGLE and st.user.is_logged_in:
        usuario_id = cuentas.seudonimo(st.user["iss"], st.user["sub"], os.environ["CUENTAS_SECRETO"])
        _registrar(usuario_id, GOOGLE)
        return usuario_id
    return None


def _entrar_mock():
    usuario_id = cuentas.seudonimo("demo", "persona-simulada", _SECRETO_MOCK)
    st.session_state[_CLAVE_MOCK] = usuario_id
    _registrar(usuario_id, MOCK)


def _salir():
    st.session_state.pop(_CLAVE_REGISTRADA, None)
    if modo() == MOCK:
        st.session_state.pop(_CLAVE_MOCK, None)
    else:
        st.logout()


def _borrar_datos():
    usuario_id = actual()
    try:
        cuentas.borrar(usuario_id)
    except sqlite3.Error as e:
        print(f"[Fuente Clara] No se pudieron borrar los datos: {e}", file=sys.stderr)
        st.toast("No pudimos borrar tus datos. Intenta de nuevo.", icon=":material/error:")
        return
    _salir()


def permitir():
    """Aplica el tope de quien consulta. Devuelve lo mismo que limites.permitir."""
    usuario_id = actual()
    if usuario_id:
        try:
            historial = cuentas.momentos(usuario_id, limites.ventana())
            tope = limites.permitir(historial)
            if not tope:
                cuentas.agregar_momento(usuario_id, historial[-1])
            return tope
        except sqlite3.Error as e:  # sin base de datos, el tope se lleva en la sesión
            print(f"[Fuente Clara] No se pudo leer el historial: {e}", file=sys.stderr)
    maximo = limites.maximo_anonimo() if modo() and not usuario_id else None
    return limites.permitir(st.session_state.setdefault("consultas", []), maximo)


def contar_consulta(modulo):
    """Suma la consulta a las métricas. Nunca debe impedir que la persona reciba su respuesta."""
    if not modo():
        return
    try:
        cuentas.contar_consulta(actual(), modulo)
    except sqlite3.Error as e:
        print(f"[Fuente Clara] No se pudo contar la consulta: {e}", file=sys.stderr)


def aviso_tope():
    """Texto para quien llegó a su tope por persona: si no tiene cuenta, le explica qué gana entrando."""
    if modo() and not actual():
        return (f"Sin cuenta puedes hacer {limites.maximo_anonimo()} consultas cada "
                f"{limites.ventana() // 60} minutos. Espera un poco o entra con tu cuenta para "
                f"hacer hasta {limites.maximo_persona()}.")
    return "Hiciste muchas consultas seguidas. Espera unos minutos y vuelve a intentarlo."


def render():
    """Barra de cuenta bajo el encabezado. Si el login no está disponible, no muestra nada."""
    forma = modo()
    if not forma:
        return
    with st.container(key="fc-cuenta"):
        boton, texto = st.columns([2, 5], vertical_alignment="center")
        demo = "Modo demostración: sin cuenta real, no se contacta a ningún proveedor. " if forma == MOCK else ""
        if not actual():
            if forma == MOCK:
                boton.button("Entrar (simulado)", key="fc-entrar", icon=":material/login:", on_click=_entrar_mock)
            else:
                boton.button("Continuar con Google", key="fc-entrar", icon=":material/login:", on_click=st.login)
            texto.caption(f"{demo}Es opcional. Con cuenta puedes hacer hasta {limites.maximo_persona()} consultas cada "
                          f"{limites.ventana() // 60} minutos. Tu cuenta no guarda tu correo, tu nombre ni lo que escribes.")
            return
        if demo:
            texto.caption(demo)
        with boton.popover("Mi cuenta", icon=":material/account_circle:"):
            st.caption("Tu cuenta guarda un código que no revela quién eres, tus fechas de ingreso y cuántas consultas "
                       f"haces por día. No guarda lo que escribes. Se elimina tras {cuentas.RETENCION_DIAS} días sin uso.")
            st.button("Cerrar sesión", key="fc-salir", icon=":material/logout:", on_click=_salir)
            st.button("Borrar mis datos y salir", key="fc-borrar", icon=":material/delete:", on_click=_borrar_datos)
