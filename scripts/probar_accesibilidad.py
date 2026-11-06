"""Prueba en un navegador real (Chromium) el panel de accesibilidad: tamaño de letra, alto contraste y lectura de la página.

Uso:  python scripts/probar_accesibilidad.py      (necesita:  pip install playwright  y  playwright install chromium;
      si ya tienes un Chrome/Chromium, indica su ruta en la variable CHROMIUM_RUTA)

Arranca la app con la IA simulada (tests/ia_simulada.py) y una voz simulada (la misma de scripts/probar_voz.py), así que no
gasta tokens ni necesita audio. Revisa: que el tamaño de letra cambie SOLO la tipografía (80/100/150/200 %, sin desbordes, en
escritorio y en 360 px), que el contraste cambie la paleta solo al llegar a 100 %, las relaciones de contraste WCAG 2.2 de los
textos en ambas paletas, la lectura de la página completa, pausar / continuar / detener, y que los lectores no se mezclen.
NO prueba el audio real ni Chrome de Android: eso se prueba a mano.
"""
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probar_voz as pv  # noqa: E402  (reutiliza la voz simulada y los helpers)

RAIZ = pv.RAIZ
PUERTO = 8597
URL = f"http://localhost:{PUERTO}"
RESULTADOS = []

# Calcula en el navegador la relación de contraste (WCAG) de los textos que se pasan, contra su fondo real.
JS_CONTRASTE = """
(selectores) => {
  const num = (c) => (c.match(/[\\d.]+/g) || []).map(Number);
  const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const lum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const fondo = (el) => { for (let e = el; e; e = e.parentElement) { const m = num(getComputedStyle(e).backgroundColor);
      if (m.length >= 3 && (m.length < 4 || m[3] > 0.5)) return m.slice(0, 3); } return [255, 255, 255]; };
  const out = {};
  for (const [nombre, sel] of Object.entries(selectores)) {
    const el = [...document.querySelectorAll(sel)].find(e => e.offsetParent !== null || getComputedStyle(e).position === 'fixed');
    if (!el) { out[nombre] = null; continue; }
    const f = fondo(el), c = num(getComputedStyle(el).color);
    let op = c.length > 3 ? c[3] : 1;
    for (let e = el; e; e = e.parentElement) op *= parseFloat(getComputedStyle(e).opacity);
    const mezcla = [0, 1, 2].map(i => c[i] * op + f[i] * (1 - op));
    const a = lum(mezcla), b = lum(f);
    out[nombre] = Math.round(((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)) * 100) / 100;
  }
  return out;
}
"""
TEXTOS = {  # nombre -> selector (todos son texto normal: mínimo 4,5:1)
    "título del documento": ".fc-doc h1", "antetítulo": ".fc-antetitulo", "bajada": ".fc-bajada", "fuente (enlace)": ".fc-fuente a",
    "párrafo": '[data-testid="stMarkdownContainer"] p', "etiqueta de campo": '[data-testid="stWidgetLabel"] p',
    "pestaña": '[data-testid="stTab"][aria-selected="false"] p', "pestaña activa": '[data-testid="stTab"][aria-selected="true"] p',
    "aviso de IA": '[data-testid="stAlert"] p', "texto del campo": "textarea", "pie": ".fc-pie",
    "leyenda (caption)": '[data-testid="stCaptionContainer"]', "aviso del dictado": ".fc-dictado-aviso",
    "encabezado de la cita (desplegable)": '[data-testid="stExpander"] summary', "recuadro de excepciones": ".fc-excepciones-lista li",
    "cita": ".fc-cita", "texto resaltado": ".fc-cita mark", "botón de lectura": '.fc-voz button[data-fc-accion="escuchar"]',
    "botón de dictado": ".fc-dictado button", "panel: nombre de control": ".fc-acc-nombre", "panel: ayuda": ".fc-acc-ayuda",
    "panel: marcas": ".fc-acc-marcas", "panel: restablecer": ".fc-acc-restablecer", "ícono flotante": ".fc-acc-flotante",
}
# Texto grande o componentes (mínimo 3:1): se miden contra su fondo.
COMPONENTES = {"borde de tarjeta vs fondo": None}


def verificar(nombre, condicion, detalle=""):
    pv.verificar(nombre, condicion, detalle)
    RESULTADOS.append((nombre, bool(condicion)))


def px(page, selector, prop="fontSize"):
    return page.evaluate("([s, p]) => { const e = [...document.querySelectorAll(s)].find(x => x.offsetParent !== null);"
                         " return e ? parseFloat(getComputedStyle(e)[p]) : null }", [selector, prop])


def caja(page, selector):
    return page.evaluate("s => { const e = [...document.querySelectorAll(s)].find(x => x.offsetParent !== null);"
                         " if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.width * 10) / 10, Math.round(r.left * 10) / 10]; }",
                         selector)


def fijar(page, id_control, valor):
    page.evaluate("([i, v]) => { const s = document.getElementById(i); s.value = v; s.dispatchEvent(new Event('input', {bubbles: true})); }", [id_control, valor])
    page.wait_for_timeout(120)


def desborda(page):
    return page.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")


def fondo_pagina(page):
    return page.evaluate("() => getComputedStyle(document.body).backgroundColor")


def preguntar(page, texto="¿Desde cuándo rige la prohibición?"):
    page.get_by_label("Tu pregunta").fill(texto)
    page.get_by_text("Estudiante").first.click()
    page.get_by_role("button", name="Explícame").last.click()
    page.get_by_role("button", name="Escuchar la respuesta en voz alta").first.wait_for(timeout=30000)
    page.wait_for_timeout(500)


def abrir_panel(page):
    if not page.locator("#fc-panel-acc.fc-visible").count():
        page.locator("#fc-btn-flotante-acc").click()
        page.wait_for_timeout(350)


def cerrar_panel(page):
    if page.locator("#fc-panel-acc.fc-visible").count():
        page.keyboard.press("Escape")
        page.wait_for_timeout(350)


def leidos(page):
    return pv.hablado(page)


def main():
    arranque = ("import sys; sys.path.insert(0, 'tests'); import ia_simulada; ia_simulada.instalar(); from streamlit.web.cli import main; "
                "sys.argv = ['streamlit', 'run', 'app.py', '--server.headless', 'true', '--server.port', '%d']; main()" % PUERTO)
    servidor = subprocess.Popen([str(RAIZ / ".venv" / "Scripts" / "python.exe"), "-c", arranque],
                                cwd=RAIZ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(URL + "/_stcore/health", timeout=1)
                break
            except OSError:
                time.sleep(1)
        with sync_playwright() as p:
            nav = p.chromium.launch(executable_path=os.getenv("CHROMIUM_RUTA") or None)

            def nueva(ancho=1000, alto=1300, voz=True):
                ctx = nav.new_context(locale="es-CL", viewport={"width": ancho, "height": alto})
                page = ctx.new_page()
                page.errores = []
                page.on("pageerror", lambda e: page.errores.append(str(e)))
                page.on("console", lambda m: page.errores.append(m.text[:160]) if m.type == "error" and "Failed to load resource" not in m.text else None)
                if voz:
                    page.add_init_script(pv.VOZ_FALSA)
                page.goto(URL)
                page.get_by_role("tab").first.wait_for(timeout=30000)
                page.locator("#fc-btn-flotante-acc").wait_for(timeout=15000)
                return page

            page = nueva()
            preguntar(page)

            # ---------------- el panel ----------------
            verificar("Panel: el botón flotante (figura de persona) está visible y tiene nombre accesible",
                      page.get_by_role("button", name="Abrir opciones de accesibilidad").is_visible())
            page.get_by_role("button", name="Abrir opciones de accesibilidad").focus()
            page.keyboard.press("Enter")
            page.wait_for_timeout(350)
            verificar("Panel: se abre con teclado y es un diálogo accesible",
                      page.locator('#fc-panel-acc[role="dialog"][aria-modal="true"].fc-visible').count() == 1)
            verificar("Panel: tiene tamaño de letra, alto contraste, lectura por voz y restablecer",
                      all(page.get_by_text(t, exact=True).first.is_visible() for t in ("Tamaño de letra", "Alto contraste", "Lectura por voz", "Restablecer preferencias"))
                      and page.get_by_role("button", name="Leer la página completa en voz alta").is_visible())
            verificar("Panel: el foco visible está definido (outline) en sus botones",
                      page.evaluate("() => { const b = document.getElementById('fc-btn-cerrar-acc'); b.focus(); return getComputedStyle(b).outlineStyle !== 'none' || b === document.activeElement; }"))
            page.keyboard.press("Escape")
            page.wait_for_timeout(350)
            verificar("Panel: Escape lo cierra y devuelve el foco al botón flotante",
                      page.locator("#fc-panel-acc.fc-visible").count() == 0
                      and page.evaluate("() => document.activeElement.id") == "fc-btn-flotante-acc")

            # ---------------- tamaño de letra ----------------
            verificar("Tamaño: rango 80–200 % en pasos de 10, inicial 100 %",
                      page.evaluate("() => { const s = document.getElementById('fc-slider-tamano'); return [s.min, s.max, s.step, s.value].join(','); }") == "80,200,10,100")
            base = {k: px(page, s) for k, s in {"h1": ".fc-doc h1", "p": '[data-testid="stMarkdownContainer"] p', "bajada": ".fc-bajada",
                                                 "etiqueta": '[data-testid="stWidgetLabel"] p', "cita": ".fc-cita", "campo": "textarea",
                                                 "boton": '[data-testid^="stBaseButton-primary"] p', "aviso": '[data-testid="stAlert"] p',
                                                 "h2": ".fc-seccion h2", "antetitulo": ".fc-antetitulo"}.items()}
            fijos = {k: caja(page, s) for k, s in {"contenedor": ".block-container", "tarjeta": ".fc-doc", "campo": "textarea", "logo": ".fc-marca img"}.items()}
            fijos["icono flotante"] = caja(page, ".fc-acc-flotante svg")
            html_base = page.evaluate("() => [getComputedStyle(document.documentElement).fontSize, getComputedStyle(document.body).zoom || '1']")
            for porcentaje in (80, 150, 200, 100):
                fijar(page, "fc-slider-tamano", porcentaje)
                esc = porcentaje / 100
                esc_titulo = 1 + (esc - 1) * 0.7
                ahora = {k: px(page, s) for k, s in {"h1": ".fc-doc h1", "p": '[data-testid="stMarkdownContainer"] p', "bajada": ".fc-bajada",
                                                      "etiqueta": '[data-testid="stWidgetLabel"] p', "cita": ".fc-cita", "campo": "textarea",
                                                      "boton": '[data-testid^="stBaseButton-primary"] p', "aviso": '[data-testid="stAlert"] p',
                                                      "h2": ".fc-seccion h2", "antetitulo": ".fc-antetitulo"}.items()}
                tipograficos_ok = all(abs(ahora[k] - base[k] * esc) <= 0.6 for k in ("p", "bajada", "etiqueta", "cita", "campo", "boton", "aviso", "antetitulo"))
                titulos_ok = all(abs(ahora[k] - base[k] * esc_titulo) <= 0.6 for k in ("h1", "h2"))
                verificar(f"Tamaño {porcentaje}%: textos proporcionales a la escala y títulos más contenidos", tipograficos_ok and titulos_ok,
                          f"{ {k: (base[k], ahora[k]) for k in base} }")
                fijos_ahora = {k: caja(page, s) for k, s in {"contenedor": ".block-container", "tarjeta": ".fc-doc", "campo": "textarea", "logo": ".fc-marca img"}.items()}
                fijos_ahora["icono flotante"] = caja(page, ".fc-acc-flotante svg")
                verificar(f"Tamaño {porcentaje}%: no cambian el ancho del contenedor, la tarjeta, el campo, el logo ni los íconos", fijos_ahora == fijos, f"{fijos} vs {fijos_ahora}")
                verificar(f"Tamaño {porcentaje}%: no hay zoom ni escala en la página y la raíz conserva su tamaño",
                          page.evaluate("() => [getComputedStyle(document.documentElement).fontSize, getComputedStyle(document.body).zoom || '1']") == html_base
                          and page.evaluate("() => getComputedStyle(document.documentElement).transform + getComputedStyle(document.body).transform") == "nonenone")
                verificar(f"Tamaño {porcentaje}%: sin desbordamiento horizontal (escritorio)", not desborda(page))
            verificar("Tamaño: al volver a 100 % los tamaños son exactamente los originales",
                      {k: px(page, s) for k, s in {"h1": ".fc-doc h1", "p": '[data-testid="stMarkdownContainer"] p'}.items()} == {"h1": base["h1"], "p": base["p"]}
                      and page.evaluate("() => document.documentElement.style.getPropertyValue('--fc-escala-texto')") == "")

            # ---------------- contraste: original vs alto ----------------
            original = fondo_pagina(page)
            colores = {}
            for valor in (0, 50, 99):
                fijar(page, "fc-slider-contraste", valor)
                colores[valor] = (fondo_pagina(page), page.evaluate("() => document.documentElement.getAttribute('data-fc-contraste')"))
                verificar(f"Contraste {valor}%: se mantienen los colores originales (sin filtros ni degradados)",
                          colores[valor] == (original, None) and original == "rgb(248, 250, 252)")
            fijar(page, "fc-slider-contraste", 100)
            alto = fondo_pagina(page)
            verificar("Contraste 100%: se activa la paleta de alto contraste (fondo oscuro)",
                      alto == "rgb(4, 19, 25)" and page.evaluate("() => document.documentElement.getAttribute('data-fc-contraste')") == "alto")
            fijar(page, "fc-slider-contraste", 99)
            verificar("Contraste de 100% a 99%: vuelve la paleta original", fondo_pagina(page) == original)
            verificar("Contraste: no se usa ningún filter en la página",
                      page.evaluate("() => [document.documentElement, document.body, document.querySelector('.stApp')].every(e => getComputedStyle(e).filter === 'none')"))
            abrir_panel(page)
            page.locator("#fc-slider-contraste").focus()
            page.keyboard.press("End")
            verificar("Contraste: con teclado (tecla Fin) se llega a 100 % y se activa", fondo_pagina(page) == "rgb(4, 19, 25)")
            page.keyboard.press("Home")
            verificar("Contraste: con teclado (tecla Inicio) vuelve a lo original", fondo_pagina(page) == original)
            cerrar_panel(page)

            # con el mouse o el dedo: arrastrar hasta el final activa el alto contraste, y soltar cerca del final lo completa
            fijar(page, "fc-slider-contraste", 0)
            abrir_panel(page)
            c = page.locator("#fc-slider-contraste").bounding_box()
            y = c["y"] + c["height"] / 2
            page.mouse.move(c["x"] + 8, y)
            page.mouse.down()
            page.mouse.move(c["x"] + c["width"] * 0.5, y)
            page.mouse.up()
            medio = page.evaluate("() => [window.__fcAcc.contraste(), document.documentElement.getAttribute('data-fc-contraste')]")
            verificar("Contraste con mouse: soltar a la mitad deja el valor ahí y los colores originales", 35 <= medio[0] <= 65 and medio[1] is None, str(medio))
            page.mouse.move(c["x"] + c["width"] * 0.5, y)
            page.mouse.down()
            page.mouse.move(c["x"] + c["width"] * 1.2, y)   # arrastrar más allá del final
            page.mouse.up()
            verificar("Contraste con mouse: arrastrar hasta el final activa el alto contraste", fondo_pagina(page) == "rgb(4, 19, 25)")
            page.locator("#fc-slider-contraste").focus()
            page.keyboard.press("ArrowLeft")
            verificar("Contraste con teclado: de 100 % a 99 % vuelve la paleta original (el imán solo actúa al soltar el puntero)",
                      page.evaluate("() => window.__fcAcc.contraste()") == 99 and fondo_pagina(page) == original)
            fijar(page, "fc-slider-contraste", 0)
            page.mouse.move(c["x"] + 8, y)
            page.mouse.down()
            page.mouse.move(c["x"] + c["width"] * 0.972, y)  # ~97-98 %: el dedo no llegó al último punto
            page.mouse.up()
            verificar("Contraste con mouse o dedo: soltar a 96–99 % completa el 100 % (en pantallas táctiles es difícil frenar justo al final)",
                      page.evaluate("() => window.__fcAcc.contraste()") == 100 and fondo_pagina(page) == "rgb(4, 19, 25)")
            verificar("Contraste: el panel dice cuánto falta y cuándo está activado",
                      "activado" in page.locator("#fc-valor-contraste").inner_text())
            fijar(page, "fc-slider-contraste", 40)
            verificar("Contraste: por debajo de 100 % el panel avisa que se activa en 100 %",
                      "se activa en 100%" in page.locator("#fc-valor-contraste").inner_text())
            cerrar_panel(page)

            # relaciones de contraste WCAG 2.2 en ambas paletas
            for nombre_paleta, valor in (("original", 0), ("alto contraste", 100)):
                fijar(page, "fc-slider-contraste", valor)
                abrir_panel(page)
                relaciones = page.evaluate(JS_CONTRASTE, TEXTOS)
                bajos = {k: v for k, v in relaciones.items() if v is not None and v < 4.5}
                verificar(f"WCAG 1.4.3 ({nombre_paleta}): todos los textos normales tienen al menos 4,5:1", not bajos, f"{bajos} de {relaciones}")
                cerrar_panel(page)
            fijar(page, "fc-slider-contraste", 100)
            componentes = page.evaluate("""() => {
              const num = (c) => (c.match(/[\\d.]+/g) || []).map(Number);
              const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
              const lum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
              const r = (a, b) => Math.round(((Math.max(lum(a), lum(b)) + 0.05) / (Math.min(lum(a), lum(b)) + 0.05)) * 100) / 100;
              const css = (n) => num(getComputedStyle(document.documentElement).getPropertyValue(n).trim() ? '' : '');
              const hex = (h) => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
              const v = (n) => hex(getComputedStyle(document.documentElement).getPropertyValue(n).trim());
              return { 'borde vs superficie': r(v('--fc-borde'), v('--fc-superficie')), 'borde vs fondo': r(v('--fc-borde'), v('--fc-fondo')),
                       'acción (foco) vs fondo': r(v('--fc-accion'), v('--fc-fondo')), 'acción vs superficie': r(v('--fc-accion'), v('--fc-superficie')) };
            }""")
            verificar("WCAG 1.4.11 (alto contraste): bordes y foco tienen al menos 3:1 contra el fondo",
                      all(x >= 3 for x in componentes.values()), str(componentes))
            fijar(page, "fc-slider-contraste", 0)
            componentes0 = page.evaluate("""() => {
              const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
              const lum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
              const r = (a, b) => Math.round(((Math.max(lum(a), lum(b)) + 0.05) / (Math.min(lum(a), lum(b)) + 0.05)) * 100) / 100;
              const hex = (h) => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
              const v = (n) => hex(getComputedStyle(document.documentElement).getPropertyValue(n).trim());
              return { 'acción (foco) vs fondo': r(v('--fc-accion'), v('--fc-fondo')), 'acción vs superficie': r(v('--fc-accion'), v('--fc-superficie')),
                       'tinta vs superficie': r(v('--fc-tinta'), v('--fc-superficie')) };
            }""")
            verificar("WCAG 1.4.11 (original): el foco y la tinta institucional tienen al menos 3:1", all(x >= 3 for x in componentes0.values()), str(componentes0))

            # ---------------- teléfono: 360 px con letra grande y alto contraste ----------------
            movil = nueva(360, 740)
            preguntar(movil)
            for porcentaje, contraste in ((150, 0), (200, 0), (200, 100)):
                fijar(movil, "fc-slider-tamano", porcentaje)
                fijar(movil, "fc-slider-contraste", contraste)
                movil.wait_for_timeout(250)
                verificar(f"Teléfono (360 px) con letra {porcentaje}% y contraste {contraste}%: sin desbordamiento horizontal", not desborda(movil),
                          str(movil.evaluate("() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]")))
            verificar("Teléfono: el panel cabe en la pantalla y se puede cerrar",
                      (lambda c: c is not None and c["x"] >= 0 and c["x"] + c["width"] <= 361)(
                          (abrir_panel(movil), movil.locator("#fc-panel-acc").bounding_box())[1]))
            cerrar_panel(movil)
            verificar("Teléfono: los botones de la lectura por voz tienen al menos 44 px de alto",
                      (abrir_panel(movil), movil.locator('#fc-panel-acc .fc-voz button:visible').first.bounding_box()["height"])[1] >= 44)
            cerrar_panel(movil)
            verificar("Teléfono: sin errores de JavaScript", not movil.errores, str(movil.errores))

            # ---------------- persistencia ----------------
            fijar(page, "fc-slider-tamano", 150)
            fijar(page, "fc-slider-contraste", 100)
            claves = page.evaluate("() => Object.keys(localStorage)")
            guardado = page.evaluate("() => localStorage.getItem('fc_preferencias_accesibilidad_v3')")
            verificar("Persistencia: solo se guardan el tamaño y el contraste (nada de audio ni de textos)",
                      guardado == '{"tamano":150,"contraste":100}' and [k for k in claves if k.startswith("fc_")] == ["fc_preferencias_accesibilidad_v3"], f"{claves} {guardado}")
            page.reload()
            page.get_by_role("tab").first.wait_for(timeout=30000)
            page.locator("#fc-btn-flotante-acc").wait_for(timeout=15000)
            page.wait_for_timeout(600)
            verificar("Persistencia: al recargar vuelven el tamaño y el alto contraste",
                      page.evaluate("() => [window.__fcAcc.tamano(), window.__fcAcc.contraste(), document.documentElement.getAttribute('data-fc-contraste')]") == [150, 100, "alto"])
            verificar("Persistencia: la lectura no empieza sola tras recargar", "speak" not in pv.acciones(page))
            abrir_panel(page)
            page.get_by_role("button", name="Restablecer preferencias").click()
            verificar("Restablecer: vuelven el tamaño 100 %, el contraste 0 % y los colores originales",
                      page.evaluate("() => [window.__fcAcc.tamano(), window.__fcAcc.contraste(), document.documentElement.getAttribute('data-fc-contraste')]") == [100, 0, None]
                      and fondo_pagina(page) == "rgb(248, 250, 252)")
            cerrar_panel(page)

            # ---------------- lectura de la página completa ----------------
            lector = nueva()
            preguntar(lector, "¿Desde cuándo rige la prohibición?")
            abrir_panel(lector)
            lector.get_by_role("button", name="Leer la página completa en voz alta").focus()
            lector.keyboard.press("Enter")
            lector.wait_for_function("() => window.__vozLog.some(e => e[0] === 'speak')")
            verificar("Página completa: se inicia con teclado, dice que está leyendo y se ven Pausar y Detener",
                      lector.locator("#fc-panel-acc .fc-voz[data-estado=leyendo]").count() == 1
                      and lector.get_by_role("button", name="Pausar la lectura").first.is_visible()
                      and lector.get_by_role("button", name="Detener la lectura").first.is_visible())
            texto = lector.evaluate("() => window.__fcVoz.recolectar()")
            verificar("Página completa: empieza por el título principal del documento", texto.startswith("Estás leyendo. Ley 21.801"), texto[:90])
            verificar("Página completa: incluye introducción, secciones y la respuesta visible",
                      all(x in texto for x in ("Explícame.", "Pregunta con tus palabras", "Respuesta simulada", "Tu colegio debe actualizar su reglamento interno")))
            verificar("Página completa: incluye las citas verificadas y sus datos",
                      "Prohíbese el uso de dispositivos móviles electrónicos" in texto and "Artículo 10 bis" in texto)
            verificar("Página completa: incluye los avisos informativos", "Esta herramienta usa inteligencia artificial" in texto)
            verificar("Página completa: no lee contenido de las pestañas no visibles",
                      not any(x in texto for x in ("Paso 2", "Paso 3", "Comparar con el texto oficial", "Preparar borrador")))
            verificar("Página completa: no lee botones, formularios, menús ni el pie",
                      not any(x in texto for x in ("Dictar con el micrófono", "Escuchar respuesta", "Terminar dictado", "Restablecer", "Tu pregunta",
                                                   "Esta herramienta solo explica el documento cargado", "Documento Ley", "Thumbs", "¿Te sirvió")))
            verificar("Página completa: no lee código, etiquetas HTML ni íconos internos",
                      not any(x in texto for x in ("<", "function", "{", "smart_toy", "material", "data-testid", "http")))
            verificar("Página completa: no lee el texto que la persona escribió en el formulario",
                      "¿Desde cuándo rige la prohibición?" not in texto.replace("sobre «¿Desde cuándo rige la prohibición?»", ""))
            pausa_antes = len(pv.acciones(lector))
            lector.get_by_role("button", name="Pausar la lectura").first.click()
            verificar("Página completa: Pausar", "pause" in pv.acciones(lector)[pausa_antes:] and lector.locator("#fc-panel-acc .fc-voz[data-estado=pausa]").count() == 1)
            lector.get_by_role("button", name="Continuar la lectura").first.click()
            verificar("Página completa: Continuar", pv.acciones(lector)[-1] == "resume" and lector.locator("#fc-panel-acc .fc-voz[data-estado=leyendo]").count() == 1)
            lector.get_by_role("button", name="Detener la lectura").first.click()
            verificar("Página completa: Detener", pv.acciones(lector)[-1] == "cancel" and lector.locator("#fc-panel-acc .fc-voz[data-estado=inactivo]").count() == 1)

            # un lector corta al otro
            cerrar_panel(lector)
            lector.get_by_role("button", name="Escuchar la respuesta en voz alta").first.click()
            lector.wait_for_function("() => window.__fcVoz.estado().estado === 'leyendo'")
            verificar("Lectores: «Escuchar respuesta» suena y el de página no", lector.locator("#fc-panel-acc .fc-voz[data-estado=leyendo]").count() == 0
                      and lector.locator(".fc-voz[data-estado=leyendo]").count() == 1)
            abrir_panel(lector)
            antes = len(pv.acciones(lector))
            lector.get_by_role("button", name="Leer la página completa en voz alta").click()
            lector.wait_for_function("n => window.__vozLog.length > n + 1", arg=antes)
            nuevos = pv.acciones(lector)[antes:]
            verificar("Lectores: leer la página cancela primero la respuesta individual", nuevos[0] == "cancel" and "speak" in nuevos, str(nuevos))
            verificar("Lectores: nunca suenan dos a la vez", lector.evaluate("() => document.querySelectorAll('.fc-voz[data-estado=leyendo]').length") == 1
                      and lector.locator("#fc-panel-acc .fc-voz[data-estado=leyendo]").count() == 1)
            cerrar_panel(lector)
            antes = len(pv.acciones(lector))
            lector.get_by_role("button", name="Escuchar la respuesta en voz alta").first.click()
            lector.wait_for_function("n => window.__vozLog.length > n + 1", arg=antes)
            verificar("Lectores: «Escuchar respuesta» cancela la lectura de la página",
                      pv.acciones(lector)[antes] == "cancel" and lector.locator("#fc-panel-acc .fc-voz[data-estado=leyendo]").count() == 0)

            # al cambiar de módulo se detiene la lectura de la página
            abrir_panel(lector)
            lector.get_by_role("button", name="Leer la página completa en voz alta").click()
            lector.wait_for_function("() => window.__fcVoz.estado().id === 'lector_global' && window.__fcVoz.estado().estado === 'leyendo'")
            cerrar_panel(lector)
            lector.get_by_role("tab", name="Verifica esto").click()
            lector.wait_for_timeout(600)
            verificar("Cambiar de módulo detiene la lectura de la página", lector.evaluate("() => window.__fcVoz.estado().estado") == "inactivo")
            abrir_panel(lector)
            lector.get_by_role("button", name="Leer la página completa en voz alta").click()
            lector.wait_for_timeout(300)
            texto2 = lector.evaluate("() => window.__fcVoz.recolectar()")
            verificar("Página completa: en otra pestaña lee solo el contenido de esa pestaña",
                      "Paso 2" in texto2 and "Verifica esto" in texto2 and "Respuesta simulada" not in texto2 and "Paso 1" not in texto2, texto2[:120])
            lector.get_by_role("button", name="Detener la lectura").first.click()
            verificar("Lectores: sin errores de JavaScript", not lector.errores and not page.errores, str(lector.errores + page.errores))

            # navegador sin síntesis de voz
            sin = nueva(voz=False)
            sin.add_init_script("delete window.speechSynthesis; delete window.SpeechSynthesisUtterance;")
            sin.reload()
            sin.get_by_role("tab").first.wait_for(timeout=30000)
            sin.locator("#fc-btn-flotante-acc").wait_for(timeout=15000)
            abrir_panel(sin)
            sin.wait_for_timeout(400)
            verificar("Sin soporte de voz: el panel avisa y deshabilita la lectura de la página",
                      "no permite escuchar" in sin.locator("#fc-panel-acc .fc-voz-estado").inner_text()
                      and sin.get_by_role("button", name="Leer la página completa en voz alta").is_disabled())
            nav.close()
    finally:
        servidor.terminate()
    fallas = [n for n, ok in RESULTADOS if not ok]
    print(f"\n{len(RESULTADOS) - len(fallas)}/{len(RESULTADOS)} comprobaciones correctas")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
