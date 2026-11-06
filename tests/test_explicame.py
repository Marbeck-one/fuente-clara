"""Explícame: cada frase se muestra solo con una cita verificada. Sin red: la IA se simula."""
import pytest

from core import documento, filtro, guardrail
from core.citas import hay_verificada
from modulos import explicame

CITA_OK = ("Prohíbese el uso de dispositivos móviles electrónicos de comunicación personal, en adelante "
           "\"dispositivos móviles\", en los establecimientos educacionales que imparten niveles de educación "
           "parvularia, básica o media.")
CITA_INVENTADA = "Este texto no aparece en ninguna parte de la ley y sirve solo para la prueba."


@pytest.fixture
def doc():
    return documento.cargar(documento.listar()[0]["archivo"])


def _simular(monkeypatch, datos):
    monkeypatch.setattr(explicame.filtro, "clasificar", lambda *a, **k: filtro.DENTRO)
    monkeypatch.setattr(explicame, "complete", lambda *a, **k: datos)


def _cita(texto):
    return {"articulo": "Artículo 10 bis", "pagina": 1, "texto_literal": texto}


def test_frase_sin_cita_verificada_no_se_muestra(monkeypatch, doc):
    _simular(monkeypatch, {"en_documento": True, "frases": [
        {"texto": "La ley prohíbe el celular en clases.", "citas": [_cita(CITA_OK)]},
        {"texto": "Además, la ley dice algo que no está.", "citas": [_cita(CITA_INVENTADA)]},
        {"texto": "Frase sin ninguna cita.", "citas": []},
    ]})
    r = explicame.explicar("¿Se puede usar el celular?", "ninguno", doc)
    assert [f["texto"] for f in r["frases"]] == ["La ley prohíbe el celular en clases."]
    assert r["frases_total"] == 3 and r["frases_sin_cita"] == 2
    assert r["respuesta"] == "La ley prohíbe el celular en clases."
    assert hay_verificada(r["citas"])


def test_la_frase_mostrada_solo_conserva_citas_verificadas(monkeypatch, doc):
    _simular(monkeypatch, {"en_documento": True, "frases": [
        {"texto": "La ley prohíbe el celular.", "citas": [_cita(CITA_INVENTADA), _cita(CITA_OK)]}]})
    r = explicame.explicar("¿Se puede usar el celular?", "ninguno", doc)
    assert len(r["frases"][0]["citas"]) == 1
    assert r["frases"][0]["citas"][0]["verificada"] is True


def test_que_cambia_solo_muestra_frases_con_cita(monkeypatch, doc):
    _simular(monkeypatch, {"en_documento": True, "frases": [
                                 {"texto": "La ley prohíbe el celular.", "citas": [_cita(CITA_OK)]}],
                           "que_cambia_para_ti": [
                               {"texto": "Tu colegio debe cambiar su reglamento.", "citas": [_cita(CITA_INVENTADA)]}]})
    r = explicame.explicar("¿Se puede usar el celular?", "Estudiante", doc)
    assert r["que_cambia_frases"] == []
    assert r["que_cambia"] == ""


def test_sin_frases_verificadas_no_hay_respuesta(monkeypatch, doc):
    _simular(monkeypatch, {"en_documento": True, "frases": [{"texto": "Algo.", "citas": [_cita(CITA_INVENTADA)]}]})
    r = explicame.explicar("¿Se puede usar el celular?", "ninguno", doc)
    assert r["frases"] == [] and not hay_verificada(r["citas"])


def test_fuera_del_documento_no_muestra_frases(monkeypatch, doc):
    _simular(monkeypatch, {"en_documento": False, "frases": [], "que_cambia_para_ti": []})
    assert explicame.explicar("¿Cuánto cuesta?", "ninguno", doc)["categoria"] == filtro.FUERA


def test_citas_a_mostrar_sin_repetidas(monkeypatch, doc):
    _simular(monkeypatch, {"en_documento": True, "frases": [
        {"texto": "Primera.", "citas": [_cita(CITA_OK)]},
        {"texto": "Segunda.", "citas": [_cita(CITA_OK)]}]})
    r = explicame.explicar("¿Se puede usar el celular?", "ninguno", doc)
    assert len(r["citas_mostrar"]) == 1 and r["citas_mostrar"][0]["verificada"] is True


def test_guardrail_quita_enlaces_de_las_frases():
    r = {"respuesta": "Mira https://ejemplo.cl",
         "frases": [{"texto": "La ley [prohíbe](https://ejemplo.cl) el celular.", "citas": []}],
         "que_cambia_frases": []}
    assert guardrail.salida_segura(r) is True
    assert "https://" not in r["frases"][0]["texto"]


def test_guardrail_bloquea_opinion_en_una_frase():
    r = {"respuesta": "Texto neutral.", "frases": [{"texto": "Te recomiendo votar por esta ley.", "citas": []}]}
    assert guardrail.salida_segura(r) is False
