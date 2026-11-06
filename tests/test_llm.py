import base64
import io
import sys
import types

import pytest
from PIL import Image

from core import llm


def test_configuracion_lee_el_entorno(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "Google")
    monkeypatch.setenv("LLM_MODEL", "modelo-x")
    assert llm.configuracion() == ("google", "modelo-x")


def test_configuracion_rechaza_proveedor_invalido(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "otro")
    with pytest.raises(llm.ErrorLLM):
        llm.configuracion()


def test_configuracion_usa_el_modelo_por_defecto(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "google")
    monkeypatch.delenv("LLM_MODEL", raising=False)
    assert llm.configuracion() == ("google", llm.MODELOS_POR_DEFECTO["google"])


def test_parsear_json_con_bloques_de_codigo_y_texto_alrededor():
    assert llm._parsear('```json\n{"a": 1}\n```') == {"a": 1}
    assert llm._parsear('Aquí está: {"a": 1} fin') == {"a": 1}


def test_parsear_falla_sin_json_o_si_no_es_objeto():
    with pytest.raises(ValueError):
        llm._parsear("sin json")
    with pytest.raises(ValueError):
        llm._parsear("[1, 2, 3]")


def test_complete_reintenta_una_vez_si_la_primera_respuesta_no_es_json(monkeypatch):
    respuestas = iter(["no es json", '{"ok": true}'])
    monkeypatch.setattr(llm, "_llamar", lambda system, user, imagen=None: next(respuestas))
    assert llm.complete("sistema", "usuario") == {"ok": True}


def test_complete_falla_si_no_hay_json_valido(monkeypatch):
    monkeypatch.setattr(llm, "_llamar", lambda system, user, imagen=None: "no es json")
    with pytest.raises(llm.ErrorLLM):
        llm.complete("sistema", "usuario")


def test_contenido_google_pone_la_imagen_primero():
    imagen = object()
    assert llm._contenido_google("texto", imagen) == [imagen, "texto"]
    assert llm._contenido_google("texto", None) == "texto"


def test_complete_reenvia_la_imagen(monkeypatch):
    vista = {}

    def falso_llamar(system, user, imagen=None):
        vista["imagen"] = imagen
        return '{"ok": true}'

    monkeypatch.setattr(llm, "_llamar", falso_llamar)
    imagen = object()
    assert llm.complete("sistema", "usuario", imagen) == {"ok": True}
    assert vista["imagen"] is imagen


def test_imagen_rechazada_si_el_proveedor_no_acepta_imagenes(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    with pytest.raises(llm.ErrorLLM):
        llm._llamar_proveedor("sistema", "usuario", imagen=object())


def test_opcionales_solo_incluye_temperatura_si_esta_definida(monkeypatch):
    monkeypatch.delenv("LLM_TEMPERATURE", raising=False)
    assert llm._opcionales() == {}
    monkeypatch.setenv("LLM_TEMPERATURE", "0.2")
    assert llm._opcionales() == {"temperature": 0.2}


def test_timeout_y_max_tokens(monkeypatch):
    monkeypatch.delenv("LLM_TIMEOUT", raising=False)
    monkeypatch.delenv("LLM_MAX_TOKENS", raising=False)
    assert llm._timeout() is None
    assert llm._max_tokens() == 3000
    monkeypatch.setenv("LLM_TIMEOUT", "12.5")
    monkeypatch.setenv("LLM_MAX_TOKENS", "500")
    assert llm._timeout() == 12.5
    assert llm._max_tokens() == 500


def test_soporta_imagenes_solo_en_anthropic_y_google(monkeypatch):
    for proveedor, esperado in [("anthropic", True), ("google", True), ("openai", False)]:
        monkeypatch.setenv("LLM_PROVIDER", proveedor)
        assert llm.soporta_imagenes() is esperado


def test_contenido_anthropic_pone_la_imagen_antes_del_texto():
    contenido = llm._contenido_anthropic("texto", Image.new("RGB", (120, 80), "white"))
    assert contenido[0]["type"] == "image"
    assert contenido[0]["source"]["media_type"] == "image/jpeg"
    assert base64.standard_b64decode(contenido[0]["source"]["data"])[:2] == b"\xff\xd8"
    assert contenido[1] == {"type": "text", "text": "texto"}
    assert llm._contenido_anthropic("texto", None) == "texto"


def test_haiku_no_recibe_temperatura(monkeypatch):
    monkeypatch.setenv("LLM_TEMPERATURE", "0")
    assert llm._opcionales("claude-haiku-5-5") == {}
    assert llm._opcionales("gemini-2.5-flash") == {"temperature": 0.0}


def test_anthropic_envia_la_imagen_en_el_mensaje(monkeypatch):
    vista = {}

    class Cliente:
        def __init__(self, **k):
            self.messages = self

        def create(self, **k):
            vista.update(k)
            return types.SimpleNamespace(content=[types.SimpleNamespace(type="text", text='{"texto": "hola"}')])

    monkeypatch.setitem(sys.modules, "anthropic", types.SimpleNamespace(Anthropic=Cliente))
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_MODEL", "claude-haiku-5-5")
    monkeypatch.setenv("LLM_TEMPERATURE", "0")
    assert llm.complete("sistema", "usuario", Image.new("RGB", (120, 80))) == {"texto": "hola"}
    assert vista["model"] == "claude-haiku-5-5"
    assert "temperature" not in vista
    bloques = vista["messages"][0]["content"]
    assert bloques[0]["type"] == "image" and bloques[1]["text"] == "usuario"
