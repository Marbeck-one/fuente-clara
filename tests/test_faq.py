"""Las dudas comunes son texto fijo: una cita que no esté en el documento debe romper la prueba, no llegar a la pantalla."""
from pathlib import Path

import pytest

from core import documento, guardrail
from core.citas import normalizar
from modulos import faq

ARCHIVOS = [d["archivo"] for d in documento.listar() if (faq.CARPETA / f"{Path(d['archivo']).stem}.yaml").exists()]


@pytest.fixture(params=ARCHIVOS)
def doc(request):
    return documento.cargar(request.param)


def test_hay_dudas_de_la_ley_21801():
    assert "ley_21801_celulares_en_colegios.pdf" in ARCHIVOS


def test_cada_documento_tiene_de_5_a_8_dudas(doc):
    assert 5 <= len(faq.leer(doc)) <= 8


def test_cada_frase_tiene_una_cita_verificada_de_8_a_40_palabras_en_un_solo_fragmento(doc):
    for duda in faq.leer(doc):
        for parte in duda["respuesta"]:
            cita = parte["cita_verificada"]
            assert cita["verificada"], f"{duda['pregunta']}: cita no encontrada: {parte['cita']}"
            assert 8 <= len(parte["cita"].split()) <= 40, parte["cita"]
            buscado = normalizar(parte["cita"]).strip(" .,;:")
            assert any(buscado in f["norm"] for f in doc["fragmentos"]), f"cruza fragmentos: {parte['cita']}"


def test_pasan_el_guardrail_de_salida(doc):
    for duda in faq.leer(doc):
        r = {"respuesta": " ".join(p["frase"] for p in duda["respuesta"]),
             "citas": [p["cita_verificada"] for p in duda["respuesta"]]}
        assert guardrail.salida_segura(r), duda["pregunta"]


def test_sin_revision_humana_no_se_publica(monkeypatch):
    dudas = [{"pregunta": "a", "revisada": False, "respuesta": [{"cita_verificada": {"verificada": True}}]},
             {"pregunta": "b", "respuesta": [{"cita_verificada": {"verificada": True}}]},
             {"pregunta": "c", "revisada": "sí", "respuesta": [{"cita_verificada": {"verificada": True}}]}]
    monkeypatch.setattr(faq, "leer", lambda doc: dudas)
    assert faq.publicables({}) == []


def test_una_cita_rota_oculta_la_duda_completa(monkeypatch):
    dudas = [{"pregunta": "rota", "revisada": True, "respuesta": [{"cita_verificada": {"verificada": True}},
                                                                  {"cita_verificada": {"verificada": False}}]},
             {"pregunta": "buena", "revisada": True, "respuesta": [{"cita_verificada": {"verificada": True}}]}]
    monkeypatch.setattr(faq, "leer", lambda doc: dudas)
    assert [d["pregunta"] for d in faq.publicables({})] == ["buena"]
