import contextlib

import pytest

from modulos import comun


@pytest.fixture
def sesion(monkeypatch):
    """Sustituye el estado de Streamlit por un diccionario simple."""
    estado = {}
    monkeypatch.setattr(comun.st, "session_state", estado)
    return estado


def test_repetido_permite_la_primera_vez_y_bloquea_la_segunda(sesion):
    assert comun.repetido("comparar|hola") is False
    assert comun.repetido("comparar|hola") is True


def test_repetido_permite_otra_accion_distinta(sesion):
    assert comun.repetido("comparar|hola") is False
    assert comun.repetido("comparar|otra cosa") is False


def test_repetido_vuelve_a_permitir_cuando_pasa_el_tiempo(sesion):
    assert comun.repetido("imagen:abc", segundos=0) is False
    assert comun.repetido("imagen:abc", segundos=0) is False


def test_firma_usa_el_nombre_y_los_argumentos_simples():
    def comparar(texto, doc):
        pass

    firma = comun._firma(comparar, ("hola", {"titulo": "no cuenta"}))
    assert firma == "comparar|hola"


def test_ejecutar_bloquea_la_misma_consulta_repetida(sesion, monkeypatch):
    monkeypatch.setattr(comun, "permitir_consulta", lambda: True)
    monkeypatch.setattr(comun.st, "spinner", lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(comun.st, "toast", lambda *a, **k: None)
    monkeypatch.setattr(comun.filtro, "revisar_respuesta", lambda r: r)
    monkeypatch.setattr(comun.votos, "traza", lambda: {"modelo": "prueba", "version": "v"})

    llamadas = []

    def comparar(texto):
        llamadas.append(texto)
        return {"categoria": "dentro_del_documento"}

    assert comun.ejecutar(comparar, "hola") is not None
    assert comun.ejecutar(comparar, "hola") is None
    assert llamadas == ["hola"]


def test_ejecutar_duplicada_devuelve_la_respuesta_que_ya_estaba(sesion, monkeypatch):
    """Al apretar dos veces el botón no se debe borrar la respuesta que ya se mostró."""
    monkeypatch.setattr(comun, "permitir_consulta", lambda: True)
    monkeypatch.setattr(comun.st, "spinner", lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(comun.st, "toast", lambda *a, **k: None)
    monkeypatch.setattr(comun.filtro, "revisar_respuesta", lambda r: r)
    monkeypatch.setattr(comun.votos, "traza", lambda: {"modelo": "prueba", "version": "v"})

    def comparar(texto):
        return {"categoria": "dentro_del_documento"}

    primera = comun.ejecutar(comparar, "hola")
    assert comun.ejecutar(comparar, "hola", previo=primera) is primera


def test_firma_distingue_el_documento():
    def comparar(texto, doc):
        pass

    assert comun._firma(comparar, ("hola", {"archivo": "a.pdf"})) != comun._firma(comparar, ("hola", {"archivo": "b.pdf"}))
