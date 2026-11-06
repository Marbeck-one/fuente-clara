"""Prueba en un navegador real (Chromium) la lectura en voz alta, con la voz y la IA simuladas.

Uso:  python scripts/probar_voz.py      (necesita:  pip install playwright  y  playwright install chromium;
      si ya tienes un Chrome/Chromium, indica su ruta en la variable CHROMIUM_RUTA)

Qué comprueba: el botón en los tres módulos, el texto exacto que se lee, teclado, pausar / continuar / detener,
que una lectura cancele la anterior, que un rerun no la reinicie, el aviso sin soporte, pantallas pequeñas y que
no haya errores de JavaScript. NO prueba el audio real ni Chrome de Android: eso se prueba a mano (ver README).
"""
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
PUERTO = 8599
URL = f"http://localhost:{PUERTO}"
RESULTADOS = []

VOZ_FALSA = """
(() => {
  const log = []; window.__vozLog = log;
  let cola = [], actual = null, pausado = false;
  class U { constructor(t) { this.text = t; this.lang = ''; this.voice = null; } }
  const ss = {
    getVoices() { return [{ lang: 'en-US', name: 'Ingles' }, { lang: 'es-CL', name: 'Chilena' }]; },
    speak(u) { log.push(['speak', u.text, u.lang]); cola.push(u); if (!actual) actual = cola.shift(); },
    cancel() { log.push(['cancel']); const a = actual; actual = null; cola = []; pausado = false;
               if (a && a.onerror) setTimeout(() => a.onerror({ error: 'interrupted' }), 0); },
    pause() { log.push(['pause']); pausado = true; },
    resume() { log.push(['resume']); pausado = false; },
    get paused() { return pausado; },
    addEventListener() {}, removeEventListener() {}
  };
  window.__terminarTrozo = () => { const u = actual; actual = null; if (u && u.onend) u.onend({}); };
  Object.defineProperty(window, 'speechSynthesis', { value: ss, configurable: true });
  window.SpeechSynthesisUtterance = U;
})();
"""


def verificar(nombre, condicion, detalle=""):
    RESULTADOS.append((nombre, bool(condicion)))
    print(f"[{'OK' if condicion else 'FALLA'}] {nombre}" + (f"  -> {detalle}" if detalle and not condicion else ""))


def hablado(page):
    return page.evaluate("() => window.__vozLog.filter(e => e[0] === 'speak').map(e => e[1])")


def acciones(page):
    return page.evaluate("() => window.__vozLog.map(e => e[0])")


def estado_ui(page):
    return page.locator(".fc-voz:visible").first.get_attribute("data-estado")


def abrir(navegador, voz=True, ancho=900):
    page = navegador.new_context(locale="es-CL", viewport={"width": ancho, "height": 900}).new_page()
    page.errores, page.malas = [], []
    page.on("response", lambda r: r.status >= 400 and page.malas.append((r.status, r.url.split("?")[0])))
    page.on("pageerror", lambda e: page.errores.append(str(e)))
    page.on("console", lambda m: m.type == "error" and "Failed to load resource" not in m.text and page.errores.append(m.text))
    if voz:
        page.add_init_script(VOZ_FALSA)
    page.goto(URL)
    page.get_by_role("tab").first.wait_for(timeout=30000)
    return page


def pestana(page, nombre):
    page.get_by_role("tab", name=nombre).click()


def main():
    # Streamlit se arranca en el mismo proceso que el parche de la IA simulada, y sirve la app real (app.py).
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
            navegador = p.chromium.launch(executable_path=os.getenv("CHROMIUM_RUTA") or None)
            page = abrir(navegador)

            # --- Explícame ---
            page.get_by_label("Tu pregunta").fill("¿Desde cuándo rige la prohibición?")
            page.get_by_text("Estudiante").first.click()
            page.get_by_role("button", name="Explícame").last.click()
            boton = page.get_by_role("button", name="Escuchar la respuesta en voz alta")
            boton.first.wait_for(timeout=20000)
            verificar("Explícame: aparece el botón «Escuchar respuesta» tras una respuesta válida", boton.count() == 1)
            texto = page.locator(".fc-voz:visible").first.get_attribute("data-fc-texto")
            verificar("Explícame: se lee la respuesta", "Respuesta simulada sobre" in texto and "prohíbe el uso" in texto)
            verificar("Explícame: se lee «qué cambia para ti»", "Tu colegio debe actualizar su reglamento interno" in texto)
            verificar("Explícame: se lee la cita verificada con su artículo", "Artículo 10 bis" in texto and "Prohíbese el uso de dispositivos" in texto)
            verificar("Explícame: no se lee HTML, Markdown, enlaces ni menús",
                      not any(x in texto for x in ("<", "**", "http", "Paso 1", "Verifica esto", "Pregúntale al Estado", "Escuchar", "Votar")))
            verificar("No empieza solo", "speak" not in acciones(page))

            # teclado: foco en el botón y Enter
            boton.first.focus()
            page.keyboard.press("Enter")
            page.wait_for_function("() => window.__vozLog.some(e => e[0] === 'speak')")
            verificar("Se inicia con teclado (Enter)", estado_ui(page) == "leyendo")
            verificar("Usa voz en español (es-CL)", all(e[2] == "es-CL" for e in page.evaluate("() => window.__vozLog.filter(e => e[0]==='speak')")))
            verificar("El foco pasa a «Pausar» al ocultarse «Escuchar»",
                      page.evaluate("() => document.activeElement.getAttribute('data-fc-accion')") == "pausar")
            verificar("Estado dicho con texto (no solo color)", "Leyendo" in page.locator(".fc-voz-estado:visible").first.inner_text())

            page.keyboard.press("Space")  # Pausar
            verificar("Pausar", "pause" in acciones(page) and estado_ui(page) == "pausa")
            verificar("En pausa se ofrece «Continuar»", page.get_by_role("button", name="Continuar la lectura").first.is_visible())
            page.get_by_role("button", name="Continuar la lectura").first.click()
            verificar("Continuar", "resume" in acciones(page) and estado_ui(page) == "leyendo")
            page.get_by_role("button", name="Detener la lectura").first.click()
            verificar("Detener", acciones(page)[-1] == "cancel" and estado_ui(page) == "inactivo")
            verificar("Al detener vuelve «Escuchar respuesta»", boton.first.is_visible())

            # termina sola: se avanza trozo por trozo hasta el final
            boton.first.click()
            page.wait_for_function("() => window.__vozLog.some(e => e[0] === 'speak')")
            for _ in range(60):
                if estado_ui(page) != "leyendo":
                    break
                page.evaluate("() => window.__terminarTrozo()")
                page.wait_for_timeout(120)
            verificar("Al terminar la lectura se restablece el estado visual",
                      estado_ui(page) == "inactivo" and "terminada" in page.locator(".fc-voz-estado:visible").first.inner_text())

            # un rerun (votar) no reinicia la lectura
            hablados = len(hablado(page))
            boton.first.click()
            page.wait_for_function("n => window.__vozLog.filter(e => e[0]==='speak').length > n", arg=hablados)
            antes = len(page.evaluate("() => window.__vozLog"))
            page.locator('button[aria-label="Thumbs up"]:visible').first.click()
            page.wait_for_timeout(1500)
            despues = len(page.evaluate("() => window.__vozLog"))
            if despues != antes:
                print("   registro:", page.evaluate("() => window.__vozLog.map(e => e[0]).join(',')"))
            verificar("Un rerun de Streamlit no reinicia ni corta la lectura",
                      despues == antes and estado_ui(page) == "leyendo", f"acciones antes={antes} despues={despues} estado={estado_ui(page)}")

            # una consulta nueva (otra respuesta) detiene la lectura anterior
            page.get_by_label("Tu pregunta").fill("¿Qué les toca hacer a los apoderados?")
            page.get_by_role("button", name="Explícame").last.click()
            page.wait_for_function("() => window.__vozLog.some(e => e[0] === 'cancel')", timeout=20000)
            verificar("Una respuesta nueva cancela la lectura de la anterior", "cancel" in acciones(page))

            # --- Verifica esto: leer cancela lo anterior y hay una sola lectura a la vez ---
            pestana(page, "Verifica esto")
            page.get_by_label("Texto a comparar").fill("Los celulares están prohibidos en los colegios")
            page.get_by_role("button", name="Comparar con el texto oficial").click()
            page.locator(".fc-voz:visible").first.wait_for(timeout=20000)
            texto_v = page.locator(".fc-voz:visible").first.get_attribute("data-fc-texto")
            verificar("Verifica: se lee afirmación, etiqueta, texto oficial y cita",
                      all(x in texto_v for x in ("Los celulares están prohibidos", "El texto lo respalda", "La ley prohíbe los dispositivos", "Prohíbese el uso")))
            verificar("Verifica: la etiqueta se lee sin símbolos", "＝" not in texto_v)
            page.locator(".fc-voz:visible").first.get_by_role("button", name="Escuchar la respuesta en voz alta").click()
            page.wait_for_timeout(300)
            hablando = page.evaluate("() => document.querySelectorAll('.fc-voz[data-estado=leyendo]').length")
            verificar("Solo una respuesta suena a la vez", hablando == 1)
            verificar("Al empezar otra se cancela la anterior antes de hablar",
                      acciones(page)[-2:] == ["cancel", "speak"] or acciones(page)[-3:-1] == ["cancel", "speak"] or "cancel" in acciones(page)[-4:])

            # --- Pregúntale al Estado ---
            pestana(page, "Pregúntale al Estado")
            page.get_by_label("Tu duda").fill("¿Cuántos colegios ya aplican la ley?")
            page.get_by_role("button", name="Preparar borrador").click()
            page.locator(".fc-voz:visible").first.wait_for(timeout=20000)
            texto_e = page.locator(".fc-voz:visible").first.get_attribute("data-fc-texto")
            verificar("Estado: se lee organismo, justificación, cita, borrador, pasos y plazos",
                      all(x in texto_e for x in ("Ministerio de Educación", "política escolar", "Lo dispuesto en el artículo 10 bis",
                                                 "Borrador de solicitud", "Pasos", "Plazos")))
            verificar("Estado: no se lee el contenido de otros módulos", "Los celulares están prohibidos" not in texto_e and "Respuesta simulada" not in texto_e)
            verificar("Estado: no se leen URLs", "http" not in texto_e)

            # tamaño de letra grande y pantalla chica
            movil = abrir(navegador, ancho=360)
            movil.get_by_label("Tu pregunta").fill("¿Desde cuándo rige?")
            movil.get_by_role("button", name="Explícame").last.click()
            movil.locator(".fc-voz:visible").first.wait_for(timeout=20000)
            movil.add_style_tag(content="html { font-size: 150% !important; }")
            movil.wait_for_timeout(300)
            caja = movil.locator(".fc-voz:visible").first.bounding_box()
            ancho_pagina = movil.evaluate("() => document.documentElement.clientWidth")
            verificar("Pantalla de 360 px con letra al 150 %: los controles caben sin desbordar",
                      caja["x"] >= 0 and caja["x"] + caja["width"] <= ancho_pagina + 1, f"{caja} / {ancho_pagina}")
            verificar("Botón de al menos 44 px de alto", movil.locator(".fc-voz button:visible").first.bounding_box()["height"] >= 44)
            verificar("Sin errores de JavaScript ni de Streamlit", not page.errores and not movil.errores, str(page.errores + movil.errores))
            malas = [m for m in page.malas + movil.malas if "/_stcore/" not in m[1] or m[0] != 404]
            verificar("Sin recursos que fallen al cargar (aparte de los sondeos internos de Streamlit)", not malas, str(malas[:5]))

            # navegador sin síntesis de voz
            sin = abrir(navegador, voz=False)
            sin.add_init_script("delete window.speechSynthesis; delete window.SpeechSynthesisUtterance;")
            sin.reload()
            sin.get_by_role("tab").first.wait_for(timeout=30000)
            sin.get_by_label("Tu pregunta").fill("¿Desde cuándo rige?")
            sin.get_by_role("button", name="Explícame").last.click()
            sin.locator(".fc-voz:visible").first.wait_for(timeout=20000)
            sin.wait_for_timeout(300)
            verificar("Sin soporte: avisa y deshabilita el botón",
                      "no permite escuchar" in sin.locator(".fc-voz-estado:visible").first.inner_text()
                      and sin.locator('.fc-voz button[data-fc-accion="escuchar"]:visible').first.is_disabled())
            verificar("Sin soporte: no hay errores de JavaScript", not sin.errores, str(sin.errores))
            navegador.close()
    finally:
        servidor.terminate()
    fallas = [n for n, ok in RESULTADOS if not ok]
    print(f"\n{len(RESULTADOS) - len(fallas)}/{len(RESULTADOS)} comprobaciones correctas")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
