"""Pruebas de interfaz con AppTest. No llaman a la IA: solo renderizan la app."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def _app():
    return AppTest.from_file(str(APP), default_timeout=60).run()


def test_aviso_de_inteligencia_artificial_visible():
    at = _app()
    assert not at.exception
    textos = [i.value for i in at.info]
    assert any("usa inteligencia artificial" in t and "Puede equivocarse" in t for t in textos)


def test_aviso_de_datos_personales_visible():
    at = _app()
    assert not at.exception
    textos = [w.value for w in at.warning]
    assert any("datos personales" in t and "proveedor de IA" in t for t in textos)


def test_camara_solo_se_monta_al_activarla():
    at = _app()
    assert not at.exception
    assert len(at.get("camera_input")) == 0

    at.button(key="ver_activar_camara").click().run()
    assert not at.exception
    assert len(at.get("camera_input")) == 1
    assert at.button(key="ver_cerrar_camara") is not None

    at.button(key="ver_cerrar_camara").click().run()
    assert not at.exception
    assert len(at.get("camera_input")) == 0
    assert at.button(key="ver_activar_camara") is not None
