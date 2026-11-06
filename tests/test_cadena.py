"""Cadena de modelos de respaldo (LLM_CADENA). Sin red: las llamadas se simulan."""
import pytest

from core import llm, votos


class Falla(Exception):
    """Error de API con código HTTP, como los de los SDK."""

    def __init__(self, codigo):
        super().__init__(f"HTTP {codigo}")
        self.status_code = codigo


@pytest.fixture
def cadena(monkeypatch):
    monkeypatch.setenv("LLM_CADENA", "anthropic:claude-a, groq:openai/gpt-oss-120b, google:gemini-x")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    monkeypatch.setenv("GROQ_API_KEY", "g")
    monkeypatch.setenv("GOOGLE_API_KEY", "x")
    monkeypatch.setenv("LLM_INTERVALO_MIN", "0")


def _simular(monkeypatch, respuestas):
    """respuestas: proveedor -> lista de lo que devuelve (texto) o lanza (excepción), en orden."""
    llamadas = []

    def falso(system, user, imagen=None, eslabon=None, reintentos=True):
        llamadas.append((eslabon[0], reintentos))
        r = respuestas[eslabon[0]].pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(llm, "_llamar_proveedor", falso)
    return llamadas


def test_lee_la_cadena_en_orden(monkeypatch):
    monkeypatch.setenv("LLM_CADENA", "Anthropic:claude-a, groq:openai/gpt-oss-120b,openai:qwen2.5:7b,")
    assert llm.cadena() == [("anthropic", "claude-a"), ("groq", "openai/gpt-oss-120b"), ("openai", "qwen2.5:7b")]
    assert llm.configuracion() == ("anthropic", "claude-a")


def test_sin_cadena_es_un_solo_modelo(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "google")
    monkeypatch.setenv("LLM_MODEL", "modelo-x")
    assert llm.cadena() == [("google", "modelo-x")]


def test_cadena_con_proveedor_invalido(monkeypatch):
    monkeypatch.setenv("LLM_CADENA", "anthropic:claude-a,inventado:modelo")
    with pytest.raises(llm.ErrorLLM):
        llm.cadena()


def test_saturado_pasa_al_siguiente_y_queda_en_pausa(monkeypatch, cadena):
    llamadas = _simular(monkeypatch, {"anthropic": [Falla(429)], "groq": ['{"ok": 1}']})
    assert llm.complete("s", "u") == {"ok": 1}
    assert [p for p, _ in llamadas] == ["anthropic", "groq"]
    assert llm.pausado(("anthropic", "claude-a"))
    assert llm.ultimo_modelo() == ("groq", "openai/gpt-oss-120b")
    assert all(not reintentos for _, reintentos in llamadas)  # en cadena los SDK no reintentan solos


def test_un_modelo_en_pausa_se_salta(monkeypatch, cadena):
    llamadas = _simular(monkeypatch, {"anthropic": [Falla(401)], "groq": ['{"a": 1}', '{"b": 2}']})
    llm.complete("s", "u")
    assert llm.complete("s", "u") == {"b": 2}
    assert [p for p, _ in llamadas] == ["anthropic", "groq", "groq"]


def test_si_todos_estan_en_pausa_igual_se_prueban(monkeypatch, cadena):
    for e in llm.cadena():
        llm._pausar(e, 60)
    _simular(monkeypatch, {"anthropic": ['{"ok": 1}']})
    assert llm.complete("s", "u") == {"ok": 1}


def test_sin_clave_se_salta(monkeypatch, cadena):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    llamadas = _simular(monkeypatch, {"groq": ['{"ok": 1}']})
    assert llm.complete("s", "u") == {"ok": 1}
    assert [p for p, _ in llamadas] == ["groq"]


def test_respuesta_sin_json_se_reintenta_en_el_mismo_modelo(monkeypatch, cadena):
    llamadas = _simular(monkeypatch, {"anthropic": ["no es json", '{"ok": 1}']})
    assert llm.complete("s", "u") == {"ok": 1}
    assert [p for p, _ in llamadas] == ["anthropic", "anthropic"]


def test_si_todos_fallan_dice_por_que(monkeypatch, cadena):
    _simular(monkeypatch, {"anthropic": [Falla(500)], "groq": [Falla(429)], "google": [TimeoutError("lento")]})
    with pytest.raises(llm.ErrorLLM) as e:
        llm.complete("s", "u")
    assert "anthropic/claude-a" in str(e.value) and "groq/" in str(e.value) and "google/" in str(e.value)
    assert not llm.pausado(("anthropic", "claude-a"))  # un error 500 no pausa: puede ser pasajero


def test_las_imagenes_van_solo_a_modelos_que_las_leen(monkeypatch, cadena):
    llamadas = _simular(monkeypatch, {"anthropic": ['{"ok": 1}']})
    assert llm.complete("s", "u", imagen=object()) == {"ok": 1}
    assert [p for p, _ in llamadas] == ["anthropic"]


def test_imagen_sin_modelo_que_la_lea(monkeypatch, cadena):
    monkeypatch.setenv("LLM_CADENA", "groq:openai/gpt-oss-120b,deepseek:deepseek-chat")
    with pytest.raises(llm.ErrorLLM):
        llm.complete("s", "u", imagen=object())


def test_un_solo_modelo_reintenta_hasta_3_veces_con_espera(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_INTERVALO_MIN", "0")
    esperas = []
    monkeypatch.setattr(llm.time, "sleep", esperas.append)
    llamadas = _simular(monkeypatch, {"anthropic": [ConnectionError("red"), ConnectionError("red"), '{"ok": 1}']})
    assert llm.complete("s", "u") == {"ok": 1}
    assert llamadas == [("anthropic", True)] * 3  # y el SDK conserva sus reintentos
    assert [s for s in esperas if s] == [1.5, 3.0]


def test_en_cadena_no_se_espera_entre_modelos(monkeypatch, cadena):
    esperas = []
    monkeypatch.setattr(llm.time, "sleep", esperas.append)
    _simular(monkeypatch, {"anthropic": [Falla(500)], "groq": ['{"ok": 1}']})
    assert llm.complete("s", "u") == {"ok": 1}
    assert not any(esperas)


def test_el_voto_registra_el_modelo_que_respondio(monkeypatch, cadena):
    _simular(monkeypatch, {"anthropic": [Falla(429)], "groq": ['{"ok": 1}']})
    llm.complete("s", "u")
    assert votos.traza()["modelo"] == "openai/gpt-oss-120b"


def test_codigo_http_de_los_sdk():
    class Google(Exception):
        code = 403
    assert llm._codigo_http(Falla(429)) == 429
    assert llm._codigo_http(Google()) == 403
    assert llm._codigo_http(ValueError("x")) is None
