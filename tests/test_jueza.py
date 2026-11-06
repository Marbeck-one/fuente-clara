"""Model routing por tarea (issue #30) e IA «jueza» (issue #29). Sin red: el modelo se simula."""
import json

import pytest

from core import filtro, jueza, llm, prompts


# ---------- #30: un modelo por tarea ----------

def test_sin_cadena_propia_la_tarea_usa_la_general(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_MODEL", "claude-sonnet-5-5")
    monkeypatch.delenv("LLM_CADENA_FILTRO", raising=False)
    assert llm.cadena("filtro") == llm.cadena() == [("anthropic", "claude-sonnet-5-5")]


def test_el_filtro_puede_usar_un_modelo_mas_barato(monkeypatch):
    monkeypatch.setenv("LLM_CADENA", "anthropic:claude-sonnet-5-5,anthropic:claude-haiku-5-5")
    monkeypatch.setenv("LLM_CADENA_FILTRO", "anthropic:claude-haiku-5-5")
    assert llm.cadena("filtro") == [("anthropic", "claude-haiku-5-5")]
    assert llm.cadena() == [("anthropic", "claude-sonnet-5-5"), ("anthropic", "claude-haiku-5-5")]
    assert llm.configuracion() == ("anthropic", "claude-sonnet-5-5")       # el modelo principal no cambia


def test_una_tarea_desconocida_no_lee_variables_raras(monkeypatch):
    monkeypatch.setenv("LLM_CADENA_RESPUESTA", "anthropic:claude-haiku-5-5")
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_MODEL", "claude-sonnet-5-5")
    assert llm.cadena("respuesta") == [("anthropic", "claude-sonnet-5-5")]


def test_complete_llama_al_modelo_de_la_tarea(monkeypatch):
    usados = []
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_MODEL", "claude-sonnet-5-5")
    monkeypatch.setenv("LLM_CADENA_FILTRO", "anthropic:claude-haiku-5-5")
    monkeypatch.setattr(llm, "_llamar", lambda system, user, imagen, e, reintentos=True: usados.append(e) or '{"ok": true}')
    llm.complete("s", "u", tarea="filtro")
    llm.complete("s", "u")
    assert usados == [("anthropic", "claude-haiku-5-5"), ("anthropic", "claude-sonnet-5-5")]


def test_el_filtro_pide_su_tarea(monkeypatch):
    vistas = []
    monkeypatch.setattr(filtro, "complete", lambda system, user, **k: vistas.append(k) or {"categoria": filtro.DENTRO})
    filtro.clasificar("¿Desde cuándo rige?", {"titulo": "x", "fragmentos": [], "texto": "x", "archivo": "x"})
    assert vistas == [{"tarea": "filtro"}]


# ---------- #29: la jueza ----------

RESPUESTA = {"categoria": filtro.DENTRO, "respuesta": "La ley prohíbe el celular en clases.", "excepciones": ["Salvo emergencias."],
             "citas_mostrar": [{"articulo": "Artículo 1", "pagina": 1, "texto_literal": "Prohíbese el uso...", "verificada": True}]}


@pytest.fixture
def bloqueos(monkeypatch, tmp_path):
    archivo = tmp_path / "bloqueos.jsonl"
    monkeypatch.setattr(jueza, "ARCHIVO", archivo)
    return archivo


def test_apagada_por_defecto_no_llama_a_la_ia(monkeypatch, bloqueos):
    monkeypatch.delenv("LLM_JUEZA", raising=False)
    monkeypatch.setattr(llm, "complete", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no llamar")))
    assert filtro.revisar_respuesta(dict(RESPUESTA)) == RESPUESTA
    assert not bloqueos.exists()


def test_aprueba_y_la_respuesta_se_muestra(monkeypatch, bloqueos):
    monkeypatch.setenv("LLM_JUEZA", "1")
    vistas = []
    monkeypatch.setattr(llm, "complete", lambda system, user, **k: vistas.append((system, user, k)) or {"aprobada": True, "motivo": "ninguno"})
    assert filtro.revisar_respuesta(dict(RESPUESTA))["respuesta"] == RESPUESTA["respuesta"]
    system, user, k = vistas[0]
    assert system == prompts.JUEZA and k == {"tarea": "jueza"}
    assert "La ley prohíbe el celular en clases." in user and "Excepción: Salvo emergencias." in user and "Prohíbese el uso" in user
    assert not bloqueos.exists()


def test_rechaza_no_se_muestra_y_se_cuenta_sin_texto(monkeypatch, bloqueos):
    monkeypatch.setenv("LLM_JUEZA", "1")
    monkeypatch.setattr(llm, "complete", lambda *a, **k: {"aprobada": False, "motivo": "opinion"})
    r = filtro.revisar_respuesta(dict(RESPUESTA))
    assert r == {"categoria": filtro.OPINION, "bloqueada": "jueza", "motivo_jueza": "opinion"}
    registro = json.loads(bloqueos.read_text(encoding="utf-8"))
    assert registro["motivo"] == "opinion" and registro["capa"] == "jueza" and registro["version"] == prompts.VERSION
    assert "prohíbe" not in bloqueos.read_text(encoding="utf-8")          # nunca se guarda el texto
    assert jueza.leer() == [registro]


def test_un_motivo_desconocido_se_cuenta_como_otro(monkeypatch, bloqueos):
    monkeypatch.setenv("LLM_JUEZA", "1")
    monkeypatch.setattr(llm, "complete", lambda *a, **k: {"aprobada": "false", "motivo": "lo_que_sea"})
    assert filtro.revisar_respuesta(dict(RESPUESTA))["motivo_jueza"] == "otro"


def test_si_la_jueza_falla_la_respuesta_se_muestra_igual(monkeypatch, bloqueos):
    monkeypatch.setenv("LLM_JUEZA", "1")

    def falla(*a, **k):
        raise llm.ErrorLLM("sin red")

    monkeypatch.setattr(llm, "complete", falla)
    assert filtro.revisar_respuesta(dict(RESPUESTA))["respuesta"] == RESPUESTA["respuesta"]


def test_las_reglas_fijas_van_antes_y_ahorran_la_llamada(monkeypatch, bloqueos):
    monkeypatch.setenv("LLM_JUEZA", "1")
    monkeypatch.setattr(llm, "complete", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no llamar")))
    assert filtro.revisar_respuesta({"categoria": filtro.DENTRO, "respuesta": "En mi opinión es una buena ley."})["bloqueada"] == "salida"
    assert filtro.revisar_respuesta({"categoria": filtro.OPINION}) == {"categoria": filtro.OPINION}


def test_la_traza_del_voto_sigue_nombrando_al_modelo_que_respondio(monkeypatch, bloqueos):
    monkeypatch.setenv("LLM_JUEZA", "1")

    def jueza_responde(*a, **k):
        llm._hilo.ultimo = ("anthropic", "claude-haiku-5-5")              # la jueza usa otro modelo
        return {"aprobada": True}

    monkeypatch.setattr(llm, "complete", jueza_responde)
    llm._hilo.ultimo = ("anthropic", "claude-sonnet-5-5")                  # el que escribió la respuesta
    filtro.revisar_respuesta(dict(RESPUESTA))
    assert llm.ultimo_modelo() == ("anthropic", "claude-sonnet-5-5")


def test_la_jueza_entra_en_la_version_de_las_instrucciones():
    assert "JUEZA" in open(prompts.__file__, encoding="utf-8").read().split("VERSION =")[1]
    for motivo in ("opinion", "recomendacion", "partidista", "sin_respaldo", "instrucciones"):
        assert f'"{motivo}"' in prompts.JUEZA and motivo in jueza.MOTIVOS
