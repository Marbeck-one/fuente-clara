"""Métricas de la IA «jueza» en scripts/evaluar.py (issue #29). Sin red: medir() se simula."""
from core import filtro
from scripts import evaluar


def test_explicame_informa_bloqueos_y_falsos_rechazos(monkeypatch):
    monkeypatch.setattr(evaluar, "medir", lambda *a: (
        {"categoria": filtro.OPINION, "bloqueada": "jueza", "motivo_jueza": "sin_respaldo"}, 1.0))
    filas, _, errores = evaluar.evaluar_explicame([{"tipo": "normal", "pregunta": "¿Qué dice la ley?"}], {})
    tabla = dict(filas)
    assert errores == 0
    assert tabla["Respuestas bloqueadas por la jueza"] == "1 (Afirma algo que las citas no respaldan: 1)"
    assert tabla["Falsos rechazos de la jueza (casos que debían mostrarse)"] == "1"


def test_verifica_y_estado_cuentan_los_bloqueos_de_la_jueza(monkeypatch):
    bloqueo = {"categoria": filtro.OPINION, "bloqueada": "jueza", "motivo_jueza": "opinion"}
    monkeypatch.setattr(evaluar, "medir", lambda *a: (bloqueo, 1.0))
    verifica = dict(evaluar.evaluar_verifica([{"texto": "La ley lo permite.", "esperado": "La ley lo permite."}], {})[0])
    estado = dict(evaluar.evaluar_estado([{"pregunta": "¿Cuándo sale?"}], {})[0])
    assert verifica["Falsos rechazos de la jueza (casos que debían mostrarse)"] == "1"
    assert estado["Falsos rechazos de la jueza (casos que debían mostrarse)"] == "1"
    assert verifica["Respuestas bloqueadas por la jueza"] == "1 (Opina o valora: 1)"
    assert estado["Respuestas bloqueadas por la jueza"] == "1 (Opina o valora: 1)"


def test_sin_bloqueos_no_agrega_filas_de_la_jueza(monkeypatch):
    monkeypatch.setattr(evaluar, "medir", lambda *a: (
        {"categoria": filtro.DENTRO, "citas": [{"verificada": True}]}, 1.0))
    filas, _, _ = evaluar.evaluar_explicame([{"tipo": "normal", "pregunta": "¿Qué dice la ley?"}], {})
    assert not any("jueza" in metrica.lower() for metrica, _ in filas)
