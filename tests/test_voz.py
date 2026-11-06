"""Lectura en voz alta (issue #5): qué texto se lee, cómo es el botón y que no toque la IA ni las citas.

El comportamiento en el navegador (pausar, continuar, detener, cancelar la anterior, teclado, sin soporte, pantallas
pequeñas) se prueba con scripts/probar_voz.py, que necesita Chromium.
"""
import copy
import re
from pathlib import Path

import pytest

import ia_simulada
from modulos import voz
from modulos.verifica import ETIQUETAS, es_valida

RAIZ = Path(__file__).resolve().parents[1]
CITA_OK = {"articulo": "Artículo 10 bis", "pagina": 2, "verificada": True,
           "texto_literal": "Prohíbese el uso de dispositivos móviles en los establecimientos educacionales."}
CITA_NO = {"articulo": "Artículo 99", "pagina": 9, "verificada": False,
           "texto_literal": "Texto inventado que no está en el documento."}


# ---------- limpiar ----------

def test_limpiar_quita_markdown_html_y_enlaces():
    sucio = "## Título\n- **Hola** [aquí](https://ejemplo.cl) <b>mundo</b> https://largo.cl/a/b/c `x` ![img](a.png)"
    assert voz.limpiar(sucio) == "Título Hola aquí mundo x"


def test_limpiar_tolera_vacios():
    assert voz.limpiar(None) == ""
    assert voz.limpiar("   ") == ""


# ---------- Explícame ----------

def _explicame(**extra):
    r = {"respuesta": "La ley **prohíbe** el celular.", "perfil": "Estudiante", "que_cambia": "Tu colegio cambia su reglamento.",
         "citas": [CITA_OK, CITA_NO]}
    r.update(extra)
    return r


def test_explicame_lee_respuesta_perfil_y_solo_citas_verificadas():
    texto = voz.texto_explicame(_explicame())
    assert "La ley prohíbe el celular." in texto
    assert "Qué cambia para ti, Estudiante." in texto and "Tu colegio cambia su reglamento." in texto
    assert "Artículo 10 bis" in texto and "página 2" in texto
    assert "Prohíbese el uso de dispositivos móviles" in texto
    assert "Texto inventado" not in texto and "Artículo 99" not in texto
    assert "**" not in texto


def test_explicame_sin_perfil_no_lee_que_cambia():
    assert "Qué cambia" not in voz.texto_explicame(_explicame(perfil="ninguno"))


# ---------- Verifica ----------

def _verifica():
    valida = {"afirmacion": "Los celulares están prohibidos.", "etiqueta": "respalda",
              "texto_oficial": "La ley prohíbe los dispositivos móviles.", "citas": [CITA_OK]}
    sin_cita = {"afirmacion": "Otra afirmación.", "etiqueta": "respalda", "texto_oficial": "Texto sin respaldo.", "citas": [CITA_NO]}
    return {"categoria": "dentro_del_documento", "comparaciones": [valida, sin_cita]}


def test_verifica_lee_solo_lo_que_la_pantalla_muestra_como_valido():
    texto = voz.texto_verifica(_verifica(), es_valida, ETIQUETAS)
    assert "Los celulares están prohibidos." in texto and "La ley prohíbe los dispositivos móviles." in texto
    assert "El texto lo respalda." in texto
    assert "Prohíbese el uso de dispositivos móviles" in texto
    assert "Otra afirmación" not in texto and "Texto sin respaldo" not in texto
    assert not any(s in texto for s in "＝≠∅")


def test_verifica_sin_comparaciones_validas_no_lee_nada():
    r = _verifica()
    r["comparaciones"] = r["comparaciones"][1:]
    assert voz.texto_verifica(r, es_valida, ETIQUETAS) == ""


# ---------- Pregúntale al Estado ----------

def test_estado_lee_organismo_borrador_pasos_y_plazos():
    r = {"organismo": "Ministerio de Educación", "justificacion": "Tiene a su cargo la política escolar.",
         "borrador": "Solicito información sobre [ORGANISMO]: https://x.cl", "citas": [CITA_OK]}
    cfg = {"pasos": [{"texto": "Entra al portal."}, {"texto": "Completa tus datos.", "estado": "VERIFICAR"}],
           "plazos": [{"texto": "20 días hábiles."}]}
    texto = voz.texto_estado(r, cfg)
    assert "Ministerio de Educación" in texto and "política escolar" in texto
    assert "Solicito información sobre ORGANISMO" in texto and "http" not in texto
    assert "1. Entra al portal." in texto and "2. Completa tus datos. Por verificar." in texto
    assert "Plazos. 20 días hábiles." in texto
    assert "Prohíbese el uso" in texto  # la cita verificada también se lee


# ---------- el botón ----------

def test_boton_usa_botones_html_con_nombres_accesibles_en_espanol():
    html = voz._html("Texto de prueba.", "k")
    assert html.count('<button type="button"') == 4
    for nombre in ("Escuchar la respuesta en voz alta", "Pausar la lectura", "Continuar la lectura", "Detener la lectura"):
        assert f'aria-label="{nombre}"' in html
    assert "Escuchar respuesta" in html
    assert 'role="group"' in html and 'role="status"' in html and 'aria-live="polite"' in html
    assert "<svg" not in html                      # st.html elimina los SVG: los íconos los dibuja el CSS
    assert "onclick" not in html and "tabindex" not in html  # solo <button> nativos: Enter y Espacio funcionan solos
    assert html.count(" hidden>") == 3             # en reposo solo se ve «Escuchar respuesta»


def test_boton_escapa_el_texto_para_no_romper_el_html():
    html = voz._html('Dice "hola" <script>alert(1)</script> & más', None)
    atributo = re.search(r'data-fc-texto="([^"]*)"', html).group(1)
    assert "<" not in atributo and '"' not in atributo
    assert "&quot;hola&quot;" in atributo


def test_el_mismo_texto_conserva_su_id_entre_reruns_y_otro_texto_cambia_de_id():
    ident = lambda t, k=None: re.search(r'data-fc-voz-id="(\w+)"', voz._html(t, k)).group(1)  # noqa: E731
    assert ident("uno") == ident("uno")
    assert ident("uno") != ident("dos")
    assert ident("uno", "a") != ident("uno", "b")


def test_boton_escuchar_no_dibuja_nada_sin_texto(monkeypatch):
    dibujado = []
    monkeypatch.setattr(voz.st, "html", lambda *a, **k: dibujado.append((a, k)))
    voz.boton_escuchar("   ")
    voz.boton_escuchar("**")
    assert dibujado == []
    voz.boton_escuchar("Hola")
    assert len(dibujado) == 1 and dibujado[0][1] == {"unsafe_allow_javascript": True}


def test_el_css_dibuja_un_icono_para_cada_boton():
    css = (RAIZ / "static" / "estilo.css").read_text(encoding="utf-8")
    for accion in ("escuchar", "pausar", "continuar", "detener"):
        assert re.search(rf'\.fc-voz button\[data-fc-accion="{accion}"\] \{{ --fc-icono: url\(', css), accion


# ---------- dictado por micrófono ----------

def test_boton_dictar_usa_botones_html_con_nombres_accesibles():
    html = voz._html_dictado('Tu "pregunta"')
    assert html.count('<button type="button"') == 2
    assert 'aria-label="Dictar con el micrófono"' in html and 'aria-label="Terminar el dictado"' in html
    assert 'role="group"' in html and 'role="status"' in html and 'aria-live="polite"' in html
    assert "<svg" not in html and "onclick" not in html and "tabindex" not in html
    assert 'data-fc-destino="Tu &quot;pregunta&quot;"' in html          # la etiqueta del campo va escapada
    assert html.count(" hidden>") == 1                                    # en reposo solo se ve «Dictar»


def test_el_javascript_del_dictado_no_usa_red_ni_almacenamiento():
    js = re.sub(r"/\*.*?\*/", "", (RAIZ / "static" / "dictado.js").read_text(encoding="utf-8"), flags=re.S)
    for prohibido in ("fetch(", "XMLHttpRequest", "WebSocket", "sendBeacon", "localStorage", "sessionStorage", "indexedDB",
                      "document.cookie", "MediaRecorder", "getUserMedia", "eval(", "new Function", "http://", "https://"):
        assert prohibido not in js, prohibido


def test_el_dictado_usa_el_reconocimiento_del_navegador_en_espanol_y_pide_conexion_segura():
    js = (RAIZ / "static" / "dictado.js").read_text(encoding="utf-8")
    for pieza in ("SpeechRecognition", "webkitSpeechRecognition", '"es-CL"', "isSecureContext", ".start()", ".stop()", ".abort()"):
        assert pieza in js, pieza
    assert "autostart" not in js.lower()


def test_la_declaracion_de_ia_dice_que_el_audio_del_dictado_sale_del_dispositivo():
    texto = (RAIZ / "DECLARACION_IA.md").read_text(encoding="utf-8")
    assert "Dictar la pregunta" in texto and "El audio sale del dispositivo" in texto


# ---------- privacidad ----------

def test_el_javascript_no_usa_red_ni_almacenamiento():
    js = re.sub(r"/\*.*?\*/", "", (RAIZ / "static" / "voz.js").read_text(encoding="utf-8"), flags=re.S)  # sin comentarios
    for prohibido in ("fetch(", "XMLHttpRequest", "WebSocket", "sendBeacon", "localStorage", "sessionStorage",
                      "indexedDB", "document.cookie", "MediaRecorder", "getUserMedia", "eval(", "new Function", "http://", "https://"):
        assert prohibido not in js, prohibido


def test_el_javascript_usa_la_api_pedida_y_la_voz_chilena_primero():
    js = (RAIZ / "static" / "voz.js").read_text(encoding="utf-8")
    for pieza in ("speechSynthesis", "SpeechSynthesisUtterance", ".speak(", ".pause()", ".resume()", ".cancel()",
                  "getVoices()", "voiceschanged", '"es-cl"', "u.rate = 1.0", "u.pitch = 1.0", "u.volume = 1.0"):
        assert pieza in js, pieza
    assert js.index('"es-cl"') < js.index('"es-419"')  # primero es-CL, después otras variantes de español


def test_voz_no_importa_ni_llama_a_la_ia():
    fuente = (RAIZ / "modulos" / "voz.py").read_text(encoding="utf-8")
    assert "core.llm" not in fuente and "complete(" not in fuente and "anthropic" not in fuente.lower().replace("anthropic.", "")


def test_armar_el_texto_no_modifica_la_respuesta_ni_sus_citas():
    r = _explicame()
    antes = copy.deepcopy(r)
    voz.texto_explicame(r)
    assert r == antes
    v = _verifica()
    antes_v = copy.deepcopy(v)
    voz.texto_verifica(v, es_valida, ETIQUETAS)
    assert v == antes_v


# ---------- integración en la app (sin red: IA simulada) ----------

@pytest.fixture
def app(monkeypatch):
    from streamlit.testing.v1 import AppTest

    llamadas = []

    def falsa(system, user, imagen=None):
        llamadas.append(system)
        return ia_simulada.falsa(system, user, imagen)

    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "simulada")
    monkeypatch.setenv("VOTOS_ARCHIVO", str(Path(__import__("tempfile").gettempdir()) / "votos_test_voz.jsonl"))
    for modulo in ("core.filtro", "modulos.explicame", "modulos.verifica", "modulos.transparencia"):
        monkeypatch.setattr(f"{modulo}.complete", falsa)
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=60).run()
    return at, llamadas


def _botones_de_voz(at):
    return [e.value for e in at.get("html") if "fc-voz" in str(e.value) and 'data-fc-texto="' in str(e.value)]


def test_el_boton_no_aparece_antes_de_preguntar(app):
    at, _ = app
    assert _botones_de_voz(at) == []


def test_explicame_muestra_el_boton_con_el_texto_correcto_y_sin_gastar_tokens_extra(app):
    at, llamadas = app
    at.text_area[0].set_value("¿Desde cuándo rige la prohibición?")
    at.pills[0].set_value("Estudiante")
    [b for b in at.button if "Explícame" in (b.label or "")][0].click().run()
    botones = _botones_de_voz(at)
    assert len(botones) == 1
    assert "Prohíbese el uso de dispositivos móviles" in botones[0] and "Artículo 10 bis" in botones[0]
    assert llamadas == [ia_simulada.prompts.FILTRO, ia_simulada.prompts.EXPLICAME]  # el botón no agrega llamadas a la IA
    at.run()  # un rerun cualquiera tampoco llama a la IA
    assert len(llamadas) == 2


def test_cada_campo_de_texto_tiene_su_boton_de_dictado_apuntando_a_su_etiqueta(app):
    at, llamadas = app
    destinos = [re.search(r'data-fc-destino="([^"]*)"', str(e.value)).group(1)
                for e in at.get("html") if 'class="fc-dictado"' in str(e.value)]
    assert destinos == ["Tu pregunta", "Texto a comparar", "Tu duda"]
    assert set(destinos) <= {a.label for a in at.text_area}  # cada botón apunta a un campo que existe
    assert llamadas == []  # dictar no llama a la IA


def test_verifica_y_estado_muestran_el_boton(app):
    at, llamadas = app
    at.text_area(key="ver_texto").set_value("Los celulares están prohibidos en los colegios")
    [b for b in at.button if "Comparar con el texto oficial" in (b.label or "")][0].click().run()
    assert len(_botones_de_voz(at)) == 1 and "El texto lo respalda" in _botones_de_voz(at)[0]
    at.text_area(key="duda_estado").set_value("¿Cuántos colegios ya aplican la ley?")
    [b for b in at.button if "Preparar borrador" in (b.label or "")][0].click().run()
    botones = _botones_de_voz(at)
    assert len(botones) == 2 and "Ministerio de Educación" in botones[1] and "Borrador de solicitud" in botones[1]
    assert "Los celulares están prohibidos" not in botones[1]  # cada botón lee solo su módulo
    assert not at.exception
