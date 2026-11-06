"""Panel de accesibilidad: tamaño de letra, alto contraste y lectura de la página.

El comportamiento en el navegador (rango del control, que solo cambie la tipografía, 0–99 % igual al original, 100 % alto
contraste, desbordes, lectura de la página y pausa) se prueba con scripts/probar_accesibilidad.py, que necesita Chromium.
"""
import re
from pathlib import Path

import pytest

from modulos import accesibilidad, voz

RAIZ = Path(__file__).resolve().parents[1]
CSS = (RAIZ / "static" / "estilo.css").read_text(encoding="utf-8")
JS_CON_COMENTARIOS = (RAIZ / "static" / "accesibilidad.js").read_text(encoding="utf-8")


def sin_comentarios_js(codigo):
    return re.sub(r"(?m)^\s*//[^\n]*$|\s//\s[^\n]*$", "", re.sub(r"/\*.*?\*/", "", codigo, flags=re.S))


JS = sin_comentarios_js(JS_CON_COMENTARIOS)


def _tokens(bloque):
    return {m.group(1): m.group(2) for m in re.finditer(r"--fc-([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})", bloque)}


def _bloque(inicio):
    desde = CSS.index(inicio)
    return CSS[desde:CSS.index("\n}", desde)]


ORIGINAL = _tokens(_bloque(":root {"))
ALTO = {**ORIGINAL, **_tokens(_bloque('html[data-fc-contraste="alto"] {'))}


def _luminancia(hexa):
    canales = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def relacion(a, b):
    la, lb = _luminancia(a), _luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


# Combinaciones que la interfaz usa de verdad: (color del texto, fondo donde se pone)
TEXTOS = [("texto", "fondo"), ("texto", "superficie"), ("texto", "campo"), ("texto-2", "superficie"), ("texto-2", "fondo"),
          ("texto-2", "campo"), ("texto-3", "superficie"), ("texto-3", "fondo"), ("accion", "superficie"), ("accion", "fondo"),
          ("tinta", "superficie"), ("tinta", "campo"), ("superficie", "tinta"), ("resaltador-texto", "resaltador"),
          ("aviso-texto", "aviso-fondo")]


@pytest.mark.parametrize("paleta,nombre", [(ORIGINAL, "original"), (ALTO, "alto contraste")])
@pytest.mark.parametrize("texto,fondo", TEXTOS)
def test_textos_cumplen_wcag_aa(paleta, nombre, texto, fondo):
    assert relacion(paleta[texto], paleta[fondo]) >= 4.5, (nombre, texto, fondo)


@pytest.mark.parametrize("paleta,nombre", [(ORIGINAL, "original"), (ALTO, "alto contraste")])
def test_foco_e_indicadores_cumplen_3_a_1(paleta, nombre):
    for fondo in ("fondo", "superficie"):
        assert relacion(paleta["accion"], paleta[fondo]) >= 3, (nombre, fondo)
    assert relacion(paleta["tinta"], paleta["superficie"]) >= 3, nombre


def test_en_alto_contraste_los_bordes_se_distinguen_del_fondo():
    for fondo in ("fondo", "superficie"):
        assert relacion(ALTO["borde"], ALTO[fondo]) >= 3


def test_la_paleta_de_alto_contraste_es_oscura_y_parte_de_los_colores_institucionales():
    assert _luminancia(ALTO["fondo"]) < 0.02 and _luminancia(ALTO["superficie"]) < 0.03
    assert ORIGINAL["tinta"] == "#083344" and ORIGINAL["fondo"] == "#F8FAFC"  # la paleta original no cambió


def test_el_alto_contraste_depende_solo_de_un_atributo_y_no_usa_filtros_ni_zoom():
    assert 'html[data-fc-contraste="alto"]' in CSS
    sin_comentarios = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
    assert not re.search(r"filter\s*:\s*[^;]*contrast", sin_comentarios)
    assert not re.search(r"(^|[;{\s])zoom\s*:", sin_comentarios)
    for selector, cuerpo in re.findall(r"([^{}]+)\{([^{}]*)\}", sin_comentarios):  # ninguna regla de la página entera escala
        if re.fullmatch(r"\s*(html|body|\.stApp|\.block-container|\[data-testid=\"stApp\"\])\s*", selector):
            assert not re.search(r"transform|zoom|scale", cuerpo), selector


def test_la_raiz_ya_no_cambia_de_tamano_solo_se_escalan_los_textos():
    sin_comentarios = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
    assert not re.search(r"html\s*\{[^}]*font-size", sin_comentarios)
    assert "--fc-escala-texto" in sin_comentarios and "--fc-escala-titulo" in sin_comentarios
    assert "max-width: 46rem" in sin_comentarios        # el ancho de la página no depende de la escala
    # todos los font-size en rem de los textos pasan por la escala, salvo el panel de accesibilidad (que no debe crecer
    # con lo que controla) y los íconos de las pestañas
    sueltos = [selector.strip() for selector, cuerpo in re.findall(r"([^{}]+)\{([^{}]*)\}", sin_comentarios)
               if re.search(r"font-size:\s*[0-9.]+rem", cuerpo) and "fc-acc" not in selector and 'span[role="img"]' not in selector]
    assert sueltos == [], sueltos


def test_el_titulo_crece_menos_que_el_texto():
    assert re.search(r"--fc-escala-titulo:\s*calc\(1 \+ \(var\(--fc-escala-texto\) - 1\) \* \.7\)", CSS)


def test_el_control_de_tamano_va_de_80_a_200_de_10_en_10_y_el_de_contraste_activa_en_100():
    assert "min: 80, max: 200, paso: 10, inicial: 100" in JS
    assert 'id="fc-slider-contraste" class="fc-acc-deslizador" min="0" max="100" step="1"' in JS
    assert "v >= 100" in JS and 'setAttribute("data-fc-contraste", "alto")' in JS
    assert "IMAN_CONTRASTE = 96" in JS and 'addEventListener("pointerup"' in JS      # solo al soltar el puntero, no con el teclado
    assert "style.filter" not in JS and "zoom" not in JS and "transform" not in JS


def test_el_panel_solo_guarda_tamano_y_contraste_y_no_empieza_a_leer_solo():
    assert "tamano: Number(sTamano.value), contraste: Number(sContraste.value)" in JS
    codigo = re.sub(r"/\*.*?\*/", "", JS, flags=re.S)
    assert codigo.count("localStorage") == 2             # una lectura y una escritura de las preferencias
    for prohibido in ("fetch(", "XMLHttpRequest", "speechSynthesis", "getUserMedia", "MediaRecorder"):
        assert prohibido not in JS, prohibido


def test_el_panel_tiene_los_controles_pedidos_con_nombres_accesibles():
    for pieza in ("Tamaño de letra", "Alto contraste", "Lectura por voz", "Leer página completa", "Restablecer preferencias",
                  '"Pausar la lectura"', '"Continuar la lectura"', '"Detener la lectura"',
                  '"Leer la página completa en voz alta"', 'aria-label="Abrir opciones de accesibilidad"',
                  'role="dialog" aria-modal="true"', "Escape"):
        assert pieza in JS, pieza


# ---------- el HTML que va a Streamlit ----------

@pytest.mark.parametrize("archivo", ["accesibilidad.js", "voz.js", "dictado.js"])
def test_los_scripts_incrustados_no_tienen_etiquetas_que_el_sanitizador_de_streamlit_borre(archivo):
    """Streamlit (DOMPurify) elimina todo <script> cuyo texto parezca contener una etiqueta HTML."""
    codigo = voz.incrustar_js((RAIZ / "static" / archivo).read_text(encoding="utf-8"))
    assert not re.search(r"<[/\w!]", codigo), archivo
    assert "</script" not in codigo.lower()


def test_incrustar_js_conserva_el_significado_del_codigo():
    assert voz.incrustar_js('x = "<div>a</div>"; if (a < b) {}') == 'x = "\\u003Cdiv>a\\u003C/div>"; if (a < b) {}'


def test_render_panel_instala_el_lector_y_el_panel_con_la_misma_clave(monkeypatch):
    html = []
    monkeypatch.setattr(accesibilidad.st, "html", lambda cuerpo, **k: html.append((cuerpo, k)))
    monkeypatch.setattr(voz.st, "html", lambda cuerpo, **k: html.append((cuerpo, k)))
    accesibilidad.render_panel("mi_lector")
    assert len(html) == 2 and all(k == {"unsafe_allow_javascript": True} for _, k in html)
    assert 'window.__fcVozPagina = "mi_lector"' in html[0][0]
    assert 'data-fc-voz-id=\\"mi_lector\\"' in html[1][0] or "mi_lector" in html[1][0]
    assert "__LECTOR__" not in html[1][0]
    assert accesibilidad.render_interruptor is accesibilidad.render_panel   # el nombre antiguo que usa app.py sigue funcionando


def test_lector_pagina_usa_una_clave_por_defecto_y_no_lee_nada_por_si_solo(monkeypatch):
    html = []
    monkeypatch.setattr(voz.st, "html", lambda cuerpo, **k: html.append(cuerpo))
    voz.lector_pagina()
    assert 'window.__fcVozPagina = "lector_global"' in html[0]
    assert ".speak(" in html[0]                           # el controlador solo habla cuando alguien toca un botón...
    js = (RAIZ / "static" / "voz.js").read_text(encoding="utf-8")
    assert js.count("leerPagina();") == 1                  # ...y solo el manejador de clics llama a leerPagina


def test_la_app_monta_el_panel_sin_errores(monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "simulada")
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=60).run()
    assert not at.exception
    cuerpos = [str(e.value) for e in at.get("html")]
    assert sum('host.id = "fc-accesibilidad-host"' in c for c in cuerpos) == 1
    assert sum("window.__fcVozPagina" in c for c in cuerpos) == 1


def test_la_lectura_de_pagina_no_usa_innertext_del_body_y_excluye_lo_que_no_se_debe_leer():
    js = sin_comentarios_js((RAIZ / "static" / "voz.js").read_text(encoding="utf-8"))
    assert "body.innerText" not in js and "document.body.textContent" not in js
    for excluido in ('[role="tablist"]', '[data-testid="stForm"]', ".fc-pie", ".fc-voz", ".fc-dictado", ".fc-cita--no",
                     "button", "textarea", '[data-testid="stIconMaterial"]', "script", "style"):
        assert excluido in js, excluido
    assert "function visible" in js and 'c.display === "none"' in js
