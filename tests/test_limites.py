import pytest

from core import limites


@pytest.fixture(autouse=True)
def limpiar_global():
    limites._recientes.clear()
    yield
    limites._recientes.clear()


def test_permite_hasta_el_limite_de_sesion(monkeypatch):
    monkeypatch.setenv("LIMITE_CONSULTAS_SESION", "2")
    monkeypatch.setenv("LIMITE_VENTANA_MIN", "10")
    monkeypatch.setenv("LIMITE_CONSULTAS_MINUTO", "100")
    historial = []
    assert limites.permitir(historial) is None
    assert limites.permitir(historial) is None
    assert limites.permitir(historial) == limites.SESION
    assert len(historial) == 2


def test_permite_hasta_el_limite_global(monkeypatch):
    monkeypatch.setenv("LIMITE_CONSULTAS_SESION", "100")
    monkeypatch.setenv("LIMITE_VENTANA_MIN", "10")
    monkeypatch.setenv("LIMITE_CONSULTAS_MINUTO", "1")
    assert limites.permitir([]) is None
    assert limites.permitir([]) == limites.GLOBAL


def test_el_maximo_indicado_reemplaza_al_de_sesion(monkeypatch):
    monkeypatch.setenv("LIMITE_CONSULTAS_SESION", "100")
    monkeypatch.setenv("LIMITE_CONSULTAS_MINUTO", "100")
    historial = []
    assert limites.permitir(historial, maximo=1) is None
    assert limites.permitir(historial, maximo=1) == limites.SESION


def test_valores_invalidos_usan_el_defecto(monkeypatch):
    monkeypatch.setenv("LIMITE_CONSULTAS_SESION", "no-es-un-numero")
    monkeypatch.setenv("LIMITE_CONSULTAS_MINUTO", "no-es-un-numero")
    assert limites.permitir([]) is None
