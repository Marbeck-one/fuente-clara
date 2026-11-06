"""Cuenta en la interfaz: topes, botones y que la app siga igual si el login no está disponible."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from core import cuentas, limites
from modulos import cuenta

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture(autouse=True)
def limpiar_global(monkeypatch):
    limites._recientes.clear()
    monkeypatch.setenv("LIMITE_CONSULTAS_MINUTO", "1000")
    yield
    limites._recientes.clear()


@pytest.fixture
def sesion(monkeypatch):
    estado = {}
    monkeypatch.setattr(cuenta.st, "session_state", estado)
    return estado


def _app():
    return AppTest.from_file(str(APP), default_timeout=60).run()


def _claves(at):
    return {b.key for b in at.button}


def _agotar(veces):
    return [cuenta.permitir() for _ in range(veces)]


def test_sin_login_no_hay_modo_ni_cambia_el_tope(sesion, monkeypatch):
    monkeypatch.setenv("LIMITE_CONSULTAS_SESION", "20")
    assert cuenta.modo() is None
    assert _agotar(20) == [None] * 20
    assert cuenta.permitir() == limites.SESION


def test_sin_cuenta_el_tope_es_5_y_con_cuenta_20(sesion, monkeypatch):
    monkeypatch.setenv("AUTH_MOCK", "1")
    assert _agotar(5) == [None] * 5
    assert cuenta.permitir() == limites.SESION
    assert "entra con tu cuenta" in cuenta.aviso_tope()

    cuenta._entrar_mock()
    assert _agotar(20) == [None] * 20
    assert cuenta.permitir() == limites.SESION
    assert "entra con tu cuenta" not in cuenta.aviso_tope()


def test_el_tope_con_cuenta_no_se_reinicia_al_empezar_otra_sesion(sesion, monkeypatch):
    monkeypatch.setenv("AUTH_MOCK", "1")
    cuenta._entrar_mock()
    _agotar(20)
    sesion.clear()  # recargar la página crea una sesión nueva
    cuenta._entrar_mock()
    assert cuenta.permitir() == limites.SESION


def test_el_tope_sin_cuenta_se_reinicia_al_recargar_limite_conocido(sesion, monkeypatch):
    monkeypatch.setenv("AUTH_MOCK", "1")
    _agotar(6)
    sesion.clear()
    assert cuenta.permitir() is None


def test_borrar_datos_elimina_la_cuenta_y_cierra_la_sesion(sesion, monkeypatch):
    monkeypatch.setenv("AUTH_MOCK", "1")
    cuenta._entrar_mock()
    cuenta.permitir()
    cuenta.contar_consulta("Explícame")
    assert cuentas.resumen()["cuentas"] == 1
    cuenta._borrar_datos()
    assert cuenta.actual() is None
    datos = cuentas.resumen()
    assert (datos["cuentas"], datos["con_cuenta"]) == (0, 0)


def test_las_consultas_anonimas_cuentan_sin_identificar(sesion, monkeypatch):
    monkeypatch.setenv("AUTH_MOCK", "1")
    cuenta.contar_consulta("Explícame")
    datos = cuentas.resumen()
    assert (datos["sin_cuenta"], datos["con_cuenta"], datos["cuentas"]) == (1, 0, 0)


def test_si_falla_la_base_de_datos_la_persona_igual_puede_consultar(sesion, monkeypatch, tmp_path):
    monkeypatch.setenv("AUTH_MOCK", "1")
    cuenta._entrar_mock()
    monkeypatch.setenv("CUENTAS_ARCHIVO", str(tmp_path))  # una carpeta: sqlite no puede abrirla
    assert cuenta.permitir() is None
    cuenta.contar_consulta("Explícame")


def test_google_requiere_credenciales_authlib_y_secreto(sesion, monkeypatch):
    monkeypatch.setenv("CUENTAS_SECRETO", "secreto")
    monkeypatch.setattr(cuenta.importlib.util, "find_spec", lambda nombre: object())
    monkeypatch.setattr(cuenta.st, "secrets", {"auth": {"client_id": "x"}})
    assert cuenta.modo() == cuenta.GOOGLE
    monkeypatch.setenv("CUENTAS_SECRETO", "")
    assert cuenta.modo() is None


def test_app_sin_login_no_muestra_nada_de_cuenta():
    at = _app()
    assert not at.exception
    assert "fc-entrar" not in _claves(at)


def test_app_en_mock_avisa_entra_y_sale(monkeypatch):
    monkeypatch.setenv("AUTH_MOCK", "1")
    at = _app()
    assert not at.exception
    assert any("Modo demostración" in c.value for c in at.caption)

    at.button(key="fc-entrar").click().run()
    assert not at.exception
    assert "fc-entrar" not in _claves(at)
    assert "fc-salir" in _claves(at)

    at.button(key="fc-salir").click().run()
    assert not at.exception
    assert "fc-entrar" in _claves(at)


def test_app_en_mock_borra_datos_desde_la_interfaz(monkeypatch):
    monkeypatch.setenv("AUTH_MOCK", "1")
    at = _app()
    at.button(key="fc-entrar").click().run()
    assert cuentas.resumen()["cuentas"] == 1
    at.button(key="fc-borrar").click().run()
    assert not at.exception
    assert cuentas.resumen()["cuentas"] == 0
    assert "fc-entrar" in _claves(at)
