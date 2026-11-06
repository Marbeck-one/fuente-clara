import json

import pytest

from core import filtro, votos


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_PROVIDER", "google")
    monkeypatch.setenv("LLM_MODEL", "modelo-de-prueba")
    monkeypatch.setattr(votos, "ARCHIVO", tmp_path / "votos.jsonl")
    yield


def _resultado():
    return {
        "id": "abc123",
        "documento": "documento.pdf",
        "categoria": filtro.DENTRO,
        "perfil": "ninguno",
        "entrada": "mi correo es persona@ejemplo.cl",
        "respuesta": "La ley regula el uso de celulares.",
        "citas": [{"articulo": "Artículo 1", "pagina": 1, "texto_literal": "La ley regula el uso de celulares.", "verificada": True}],
        "traza": votos.traza(),
    }


def test_ocultar_datos_personales():
    texto = "RUT 12.345.678-9, correo persona@ejemplo.cl, fono +56 9 1234 5678"
    oculto = votos.ocultar_datos(texto)
    assert "12.345.678-9" not in oculto
    assert "persona@ejemplo.cl" not in oculto
    assert "1234 5678" not in oculto
    assert "[RUT]" in oculto and "[CORREO]" in oculto and "[TELÉFONO]" in oculto


def test_traza_guarda_proveedor_modelo_y_version():
    t = votos.traza()
    assert t["proveedor"] == "google"
    assert t["modelo"] == "modelo-de-prueba"
    assert t["version"].startswith("v-")


def test_votar_no_guarda_la_pregunta_ni_la_respuesta():
    r = _resultado()
    votos.votar(r, "Explícame", bueno=True)
    registros = [json.loads(linea) for linea in votos.ARCHIVO.read_text(encoding="utf-8").splitlines()]
    assert len(registros) == 1
    assert registros[0]["tipo"] == "voto"
    assert registros[0]["voto"] == "bueno"
    assert "pregunta" not in registros[0]
    assert "respuesta" not in registros[0]


def test_detallar_sin_autorizacion_no_guarda_texto():
    r = _resultado()
    votos.votar(r, "Explícame", bueno=False)
    votos.detallar(r, "Difícil de entender", autoriza=False)
    detalle = [json.loads(linea) for linea in votos.ARCHIVO.read_text(encoding="utf-8").splitlines()][-1]
    assert detalle["tipo"] == "detalle"
    assert detalle["autoriza"] is False
    assert "pregunta" not in detalle
    assert "respuesta" not in detalle


def test_detallar_con_autorizacion_guarda_texto_sin_datos_personales():
    r = _resultado()
    votos.votar(r, "Explícame", bueno=False)
    votos.detallar(r, "Difícil de entender", autoriza=True)
    detalle = [json.loads(linea) for linea in votos.ARCHIVO.read_text(encoding="utf-8").splitlines()][-1]
    assert detalle["autoriza"] is True
    assert "persona@ejemplo.cl" not in detalle["pregunta"]
    assert "[CORREO]" in detalle["pregunta"]
    assert detalle["citas"][0]["verificada"] is True


def test_leer_une_voto_y_detalle():
    r = _resultado()
    votos.votar(r, "Explícame", bueno=False)
    votos.detallar(r, "Difícil de entender", autoriza=True)
    registros = votos.leer()
    assert len(registros) == 1
    assert registros[0]["voto"] == "malo"
    assert registros[0]["motivo"] == "Difícil de entender"


def test_resumen_para_cada_categoria():
    assert votos.resumen({"categoria": filtro.OPINION}).startswith("(El filtro")
    assert "→ [respalda]" in votos.resumen(
        {"categoria": filtro.DENTRO, "comparaciones": [{"afirmacion": "a", "etiqueta": "respalda", "texto_oficial": "b"}]})
    assert votos.resumen({"categoria": filtro.FUERA, "borrador": "B", "organismo": "O", "justificacion": "J"}).startswith("Organismo")
    assert votos.resumen({"categoria": filtro.FUERA}) == "(El documento no responde esta pregunta.)"
    assert votos.resumen({"categoria": filtro.DENTRO, "respuesta": "R", "citas": []}).startswith("(No se le mostró")
