"""Excepciones de la respuesta de Explícame: el modelo las entrega aparte y la pantalla las destaca en amarillo."""
import re
from pathlib import Path

import pytest

import ia_simulada
from core import guardrail, prompts, votos
from modulos import explicame, voz

RAIZ = Path(__file__).resolve().parents[1]


# ---------- lo que devuelve el modelo ----------

@pytest.fixture
def explicar_con(monkeypatch):
    """Corre explicar() con la respuesta que se le indique, sin red: el filtro dice «dentro del documento»."""
    from core import documento, filtro

    doc = documento.cargar("ley_21801_celulares_en_colegios.pdf")
    monkeypatch.setattr(filtro, "clasificar", lambda *a, **k: filtro.DENTRO)

    def correr(excepciones):
        cita = [{"articulo": "Artículo 10 bis", "pagina": 1, "texto_literal": ia_simulada.CITA_1}]
        datos = {"en_documento": "true", "frases": [{"texto": "Está prohibido.", "citas": cita}], "que_cambia_para_ti": [],
                 "excepciones": excepciones}
        monkeypatch.setattr(explicame, "complete", lambda *a, **k: datos)
        return explicame.explicar("¿Puedo usar el celular?", "Estudiante", doc)

    return correr


CITA_OK = [{"articulo": "Artículo 10 bis", "pagina": 1, "texto_literal": ia_simulada.CITA_1}]
CITA_FALSA = [{"articulo": "Artículo 99", "pagina": 9, "texto_literal": "Esto no aparece en el documento y nunca fue escrito por nadie allí."}]


def test_solo_se_muestran_excepciones_con_cita_verificada(explicar_con):
    r = explicar_con([{"texto": "Con permiso del director.", "citas": CITA_OK}, {"texto": "Inventada.", "citas": CITA_FALSA},
                      {"texto": "Sin cita.", "citas": []}])
    assert r["excepciones"] == ["Con permiso del director."]
    assert any(c["texto_literal"] == ia_simulada.CITA_1 for c in r["citas_mostrar"])   # su cita aparece en «De dónde sale»


@pytest.mark.parametrize("valor", [None, [], "Una frase suelta", {"a": 1}, 5, ["texto suelto"], [None, 3, "x"]])
def test_si_el_modelo_devuelve_otra_cosa_no_hay_excepciones_ni_errores(explicar_con, valor):
    assert explicar_con(valor)["excepciones"] == []


def test_como_maximo_tres_excepciones(explicar_con):
    items = [{"texto": f"Excepción {i}.", "citas": CITA_OK} for i in range(6)]
    assert explicar_con(items)["excepciones"] == ["Excepción 0.", "Excepción 1.", "Excepción 2."]


def test_una_excepcion_muy_larga_se_recorta_sin_partir_palabras(explicar_con):
    larga = ("Primera frase completa y clara. " * 10) + "Segunda parte " * 60
    corta = explicar_con([{"texto": larga, "citas": CITA_OK}])["excepciones"][0]
    assert len(corta) <= 400 and corta.endswith("clara.")                    # corta al final de una frase
    sin_puntos = explicar_con([{"texto": "palabra " * 200, "citas": CITA_OK}])["excepciones"][0]
    assert len(sin_puntos) <= 401 and sin_puntos.endswith("palabra…")           # o al final de una palabra
    assert explicar_con([{"texto": "Corta.", "citas": CITA_OK}])["excepciones"] == ["Corta."]


def test_el_prompt_pide_excepciones_solo_si_el_documento_las_establece():
    assert '"excepciones"' in prompts.EXPLICAME
    assert "Incluye solo las que el DOCUMENTO establece" in prompts.EXPLICAME
    assert "deja []" in prompts.EXPLICAME
    assert "misma forma (texto y cita)" in prompts.EXPLICAME     # cada excepción lleva su cita literal, como las frases


# ---------- guardrail capa 3 ----------

def test_las_excepciones_pasan_por_el_guardrail_de_salida():
    r = {"respuesta": "Está prohibido.", "excepciones": ["Mira [aquí](https://malo.cl) y https://otro.cl"]}
    assert guardrail.salida_segura(r) is True
    assert "http" not in r["excepciones"][0] and "aquí" in r["excepciones"][0]
    assert guardrail.salida_segura({"respuesta": "Ok.", "excepciones": ["Te recomiendo votar por esta ley."]}) is False
    assert guardrail.salida_segura({"respuesta": "Ok.", "excepciones": ["Esto es falso."]}) is False


# ---------- lo que se ve, se lee y se guarda ----------

def test_el_bloque_amarillo_muestra_cada_excepcion_escapada(monkeypatch):
    html = []
    monkeypatch.setattr(explicame.st, "html", lambda c, **k: html.append(c))
    explicame.bloque_excepciones(["Con permiso del <director>.", "En media, según el reglamento."])
    assert len(html) == 1
    cuerpo = html[0]
    assert 'class="fc-excepciones"' in cuerpo and "Hay excepciones" in cuerpo
    assert cuerpo.count("<li>") == 2 and "&lt;director&gt;" in cuerpo and "<director>" not in cuerpo
    assert 'aria-label="Excepciones que establece el documento"' in cuerpo


def test_sin_excepciones_no_se_dibuja_nada(monkeypatch):
    html = []
    monkeypatch.setattr(explicame.st, "html", lambda c, **k: html.append(c))
    explicame.bloque_excepciones([])
    explicame.bloque_excepciones(None)
    assert html == []


def test_la_voz_lee_las_excepciones_entre_la_respuesta_y_las_citas():
    r = {"respuesta": "Está prohibido.", "perfil": "ninguno", "que_cambia": "",
         "excepciones": ["Si hay una emergencia, se puede usar.", "En media, lo decide el colegio."],
         "citas_mostrar": [{"articulo": "Artículo 1", "pagina": 1, "verificada": True, "texto_literal": "Prohíbese el uso."}]}
    texto = voz.texto_explicame(r)
    assert "Hay excepciones. Si hay una emergencia, se puede usar. En media, lo decide el colegio." in texto
    assert texto.index("Está prohibido") < texto.index("Hay excepciones") < texto.index("De dónde sale")


def test_lo_que_se_guarda_al_votar_incluye_las_excepciones_que_vio_la_persona():
    from core import filtro
    r = {"categoria": filtro.DENTRO, "respuesta": "Está prohibido.", "excepciones": ["Una.", "Dos."], "perfil": "ninguno",
         "citas": [{"verificada": True}]}
    assert "Excepciones: Una. · Dos." in votos.resumen(r)
    sin = {"categoria": filtro.DENTRO, "respuesta": "Está prohibido.", "perfil": "ninguno", "citas": [{"verificada": True}]}
    assert "Excepciones" not in votos.resumen(sin)


def test_estilos_del_recuadro_amarillo_y_del_alto_contraste():
    css = (RAIZ / "static" / "estilo.css").read_text(encoding="utf-8")
    assert ".fc-excepciones {" in css and "#FEF9C3" in css and "#EAB308" in css
    assert 'html[data-fc-contraste="alto"] .fc-excepciones' in css
    assert "calc(1rem * var(--fc-escala-texto))" in css[css.index(".fc-excepciones-lista li"):]   # crece con el tamaño de letra


def _luminancia(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    l = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2]


@pytest.mark.parametrize("texto,fondo", [("#422006", "#FEF9C3"), ("#713F12", "#FEF9C3"), ("#041319", "#FACC15")])
def test_el_recuadro_amarillo_cumple_contraste_wcag_aa(texto, fondo):
    a, b = _luminancia(texto), _luminancia(fondo)
    assert (max(a, b) + 0.05) / (min(a, b) + 0.05) >= 4.5


# ---------- integración en la app (IA simulada, sin red) ----------

def test_la_app_muestra_el_recuadro_con_las_excepciones_de_la_respuesta(monkeypatch):
    from streamlit.testing.v1 import AppTest

    def falsa(system, user, imagen=None, tarea=None):
        return ia_simulada.falsa(system, user, imagen)

    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "simulada")
    monkeypatch.setenv("VOTOS_ARCHIVO", str(Path(__import__("tempfile").gettempdir()) / "votos_test_exc.jsonl"))
    for modulo in ("core.filtro", "modulos.explicame"):
        monkeypatch.setattr(f"{modulo}.complete", falsa)
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=60).run()
    at.text_area[0].set_value("¿Puedo usar el celular en el colegio?")
    [b for b in at.button if "Explícame" in (b.label or "")][0].click().run()
    cuerpos = [str(e.value) for e in at.get("html")]
    bloques = [c for c in cuerpos if 'class="fc-excepciones"' in c]
    assert len(bloques) == 1
    assert "necesidades educativas especiales" in bloques[0] and bloques[0].count("<li>") == 2
    voces = [c for c in cuerpos if 'data-fc-texto="' in c]
    assert any("Hay excepciones" in c for c in voces)       # lo que se ve también se lee
    assert not at.exception
