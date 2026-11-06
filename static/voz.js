/* Lectura en voz alta de Fuente Clara. Lo inserta modulos/voz.py dentro de cada botón "Escuchar respuesta".
 *
 * - Usa solo la síntesis de voz del navegador (window.speechSynthesis). No hace llamadas de red,
 *   no usa localStorage ni guarda audio.
 * - Hay un único controlador por página: leer una respuesta cancela la anterior.
 * - Los botones se encuentran por delegación de eventos, así que sobreviven a los reruns de Streamlit.
 * - Nunca empieza solo: siempre parte de un clic o de Enter/Espacio sobre un botón.
 */
(function () {
  "use strict";
  if (window.__fcVoz) { window.__fcVoz.pintar(); return; }

  var SOPORTADO = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
  var TROZO_MAX = 180;           // Chrome corta las lecturas largas: se leen por trozos
  var ESPERA_VOCES_MS = 1200;    // tiempo máximo esperando la lista de voces
  var TEXTOS = {
    leyendo: "Leyendo la respuesta…",
    pausa: "Lectura en pausa.",
    detenida: "Lectura detenida.",
    fin: "Lectura terminada.",
    sinPausa: "Tu navegador no permite pausar. Detuvimos la lectura.",
    sinVoz: "Este dispositivo no tiene una voz en español. Instálala en los ajustes de voz del sistema.",
    error: "No pudimos leer la respuesta en voz alta.",
    sinPagina: "No encontramos texto que leer en esta página.",
    noSoporta: "Tu navegador no permite escuchar respuestas. Puedes leerla en pantalla."
  };

  var s = { id: null, estado: "inactivo", mensaje: "", trozos: [], indice: 0, sesion: 0, voz: null };

  function grupos() { return document.querySelectorAll(".fc-voz"); }
  function idPagina() { return window.__fcVozPagina || "lector_global"; }

  function pintar() {
    grupos().forEach(function (g) {
      var propio = SOPORTADO && g.getAttribute("data-fc-voz-id") === s.id;
      var estado = propio ? s.estado : "inactivo";
      g.setAttribute("data-estado", estado);
      g.setAttribute("data-soportado", SOPORTADO ? "si" : "no");
      var botones = g.querySelectorAll("[data-fc-accion]");
      botones.forEach(function (b) {
        var a = b.getAttribute("data-fc-accion");
        var visible = (a === "escuchar" && estado === "inactivo") ||
                      (a === "pausar" && estado === "leyendo") ||
                      (a === "continuar" && estado === "pausa") ||
                      (a === "detener" && (estado === "leyendo" || estado === "pausa"));
        b.hidden = !visible;
        b.disabled = !SOPORTADO;
      });
      var msg = g.querySelector(".fc-voz-estado");
      if (msg) {
        var texto = !SOPORTADO ? TEXTOS.noSoporta : (propio ? s.mensaje : "");
        if (msg.textContent !== texto) msg.textContent = texto;   // sin cambios no se toca el DOM (evita bucles del observador)
      }
    });
  }

  function elegirVoz() {
    var voces = window.speechSynthesis.getVoices() || [];
    if (!voces.length) return { voz: null, hay: false };
    var lang = function (v) { return (v.lang || "").toLowerCase().replace("_", "-"); };
    var orden = [
      function (v) { return lang(v) === "es-cl"; },
      function (v) { return lang(v) === "es-419" || lang(v) === "es-mx" || lang(v) === "es-us"; },
      function (v) { return lang(v).indexOf("es-") === 0; },
      function (v) { return lang(v) === "es"; }
    ];
    for (var i = 0; i < orden.length; i++) {
      var v = voces.filter(orden[i])[0];
      if (v) return { voz: v, hay: true };
    }
    return { voz: null, hay: false, sinEspanol: true };
  }

  function esperarVoces(listo) {
    var ss = window.speechSynthesis;
    if ((ss.getVoices() || []).length) return listo();
    var terminado = false;
    function fin() {
      if (terminado) return;
      terminado = true;
      ss.removeEventListener && ss.removeEventListener("voiceschanged", fin);
      listo();
    }
    ss.addEventListener && ss.addEventListener("voiceschanged", fin);
    setTimeout(fin, ESPERA_VOCES_MS);
  }

  function trocear(texto) {
    var frases = String(texto).replace(/\s+/g, " ").trim().split(/(?<=[.!?:;])\s+/);
    var trozos = [], actual = "";
    function empujar() { if (actual.trim()) trozos.push(actual.trim()); actual = ""; }
    frases.forEach(function (frase) {
      while (frase.length > TROZO_MAX) {
        var corte = frase.lastIndexOf(",", TROZO_MAX);
        if (corte < 40) corte = frase.lastIndexOf(" ", TROZO_MAX);
        if (corte < 1) corte = TROZO_MAX;
        if (actual) empujar();
        trozos.push(frase.slice(0, corte + 1).trim());
        frase = frase.slice(corte + 1).trim();
      }
      if ((actual + " " + frase).length > TROZO_MAX) empujar();
      actual = actual ? actual + " " + frase : frase;
    });
    empujar();
    return trozos;
  }

  function limpiar() {
    s.sesion++;               // los eventos de lo que se cancela dejan de contar
    try { window.speechSynthesis.cancel(); } catch (e) { /* nada que cancelar */ }
  }

  function terminar(estado, mensaje) {
    s.estado = estado; s.mensaje = mensaje; s.trozos = []; s.indice = 0;
    pintar();
  }

  function hablarTrozo(sesion) {
    if (sesion !== s.sesion) return;
    if (s.indice >= s.trozos.length) { terminar("inactivo", TEXTOS.fin); return; }
    var u = new window.SpeechSynthesisUtterance(s.trozos[s.indice]);
    u.lang = s.voz ? s.voz.lang : "es-CL";
    if (s.voz) u.voice = s.voz;
    u.rate = 1.0; u.pitch = 1.0; u.volume = 1.0;
    u.onend = function () { if (sesion === s.sesion) { s.indice++; hablarTrozo(sesion); } };
    u.onerror = function (e) {
      if (sesion !== s.sesion) return;
      if (e && (e.error === "canceled" || e.error === "interrupted")) return;
      terminar("inactivo", TEXTOS.error);
    };
    window.speechSynthesis.speak(u);
  }

  function escuchar(id, texto) {
    if (!SOPORTADO || !texto) return;
    limpiar();                // una sola respuesta a la vez
    s.id = id; s.estado = "leyendo"; s.mensaje = TEXTOS.leyendo;
    s.trozos = trocear(texto); s.indice = 0;
    var sesion = s.sesion;
    pintar();
    esperarVoces(function () {
      if (sesion !== s.sesion) return;
      var e = elegirVoz();
      if (e.sinEspanol) { terminar("inactivo", TEXTOS.sinVoz); return; }
      s.voz = e.voz;
      setTimeout(function () { hablarTrozo(sesion); }, 60);  // Chrome ignora speak() inmediato a cancel()
    });
  }

  function pausar() {
    if (s.estado !== "leyendo") return;
    window.speechSynthesis.pause();
    if (window.speechSynthesis.paused) { s.estado = "pausa"; s.mensaje = TEXTOS.pausa; }
    else { limpiar(); terminar("inactivo", TEXTOS.sinPausa); }   // Chrome en Android no sabe pausar
    pintar();
  }

  function continuar() {
    if (s.estado !== "pausa") return;
    window.speechSynthesis.resume();
    s.estado = "leyendo"; s.mensaje = TEXTOS.leyendo;
    pintar();
  }

  function detener() {
    limpiar();
    terminar("inactivo", TEXTOS.detenida);
  }

  // ---------- lector de página completa ----------
  // Recorre una estructura controlada (títulos, párrafos, listas, citas, avisos) dentro del contenido principal,
  // en el orden de la pantalla. No usa body.innerText: lo oculto, los menús, los botones y los formularios no se leen.
  var RAIZ = '[data-testid="stMainBlockContainer"], [data-testid="stMain"], .block-container, main';
  var LEIBLES = "h1,h2,h3,h4,p,li,blockquote,summary,td,th,figcaption";
  var NO_LEER = [
    "script", "style", "template", "button", "textarea", "input", "select", "nav", "header", "footer",
    '[role="tablist"]', '[data-testid="stForm"]', '[data-testid="stWidgetLabel"]', '[data-testid="stFeedback"]',
    '[data-testid="stPills"]', '[data-testid="stSelectbox"]', '[data-testid="stToast"]', '[data-testid="stFileUploader"]',
    '[class*="st-key-fc-voto"]', ".fc-marca", ".fc-pie", ".fc-voz", ".fc-dictado", ".fc-cita--no", ".fc-instalador",
    ".fc-acc-panel", "#fc-accesibilidad-host", '[data-fc-no-leer]', '[aria-hidden="true"]'
  ].join(",");
  var DECORATIVO = '[data-testid="stIconMaterial"], svg, img, [aria-hidden="true"], .fc-voz, .fc-dictado, button, script, style';

  function visible(el, raiz) {
    for (var a = el; a && a !== raiz.parentElement; a = a.parentElement) {
      if (a.hidden) return false;
      var c = window.getComputedStyle(a);
      if (c.display === "none" || c.visibility === "hidden") return false;
    }
    return true;
  }

  function textoDe(el) {
    var copia = el.cloneNode(true);
    copia.querySelectorAll(DECORATIVO).forEach(function (n) { n.remove(); });
    return (copia.textContent || "").replace(/\s+/g, " ").trim();
  }

  function recolectar() {
    var raiz = document.querySelector(RAIZ);
    if (!raiz) return "";
    var partes = [], anterior = "";
    raiz.querySelectorAll(LEIBLES).forEach(function (el) {
      if (el.closest(NO_LEER) || el.querySelector(LEIBLES) || !visible(el, raiz)) return;  // solo hojas, visibles y legibles
      var texto = textoDe(el);
      if (!texto || texto === anterior) return;
      anterior = texto;
      partes.push(/[.!?:;»)]$/.test(texto) ? texto : texto + ".");
    });
    return partes.join(" ");
  }

  function leerPagina() {
    if (!SOPORTADO) return;
    var texto = recolectar();
    if (!texto) { limpiar(); s.id = idPagina(); terminar("inactivo", TEXTOS.sinPagina); return; }
    escuchar(idPagina(), texto);
  }

  function enfocarPrimero(grupo) {
    var b = grupo && grupo.querySelector("[data-fc-accion]:not([hidden])");
    if (b) b.focus();
  }

  document.addEventListener("click", function (ev) {
    var b = ev.target && ev.target.closest ? ev.target.closest("[data-fc-accion]") : null;
    if (!b) return;
    var g = b.closest(".fc-voz");
    if (!g) return;
    var accion = b.getAttribute("data-fc-accion");
    if (accion === "escuchar" && g.hasAttribute("data-fc-pagina")) leerPagina();
    else if (accion === "escuchar") escuchar(g.getAttribute("data-fc-voz-id"), g.getAttribute("data-fc-texto"));
    else if (accion === "pausar") pausar();
    else if (accion === "continuar") continuar();
    else if (accion === "detener") detener();
    enfocarPrimero(g);   // el botón pulsado se oculta: el foco pasa al siguiente para no perder el teclado
  });

  // Si la respuesta que se está leyendo sale de la pantalla (se hizo otra consulta, se cambió de
  // documento), se detiene. Se espera un momento porque Streamlit quita y vuelve a poner elementos al redibujar.
  var revisando = null;
  function revisarPresencia() {
    if (revisando) return;
    revisando = setTimeout(function () {
      revisando = null;
      if (s.estado === "inactivo" || !s.id) { pintar(); return; }
      var sigue = Array.prototype.some.call(grupos(), function (g) {
        return g.getAttribute("data-fc-voz-id") === s.id;
      });
      if (!sigue) { limpiar(); terminar("inactivo", ""); } else { pintar(); }
    }, 500);
  }
  new MutationObserver(revisarPresencia).observe(document.body, { childList: true, subtree: true });

  document.addEventListener("click", function (ev) {
    var pestana = ev.target && ev.target.closest ? ev.target.closest('[role="tab"]') : null;
    if (pestana && SOPORTADO && s.id === idPagina() && s.estado !== "inactivo") detener();
  }, true);   // en la fase de captura: React Aria detiene la propagación de los clics de las pestañas

  window.addEventListener("pagehide", function () { if (SOPORTADO) limpiar(); });

  window.__fcVoz = { pintar: pintar, recolectar: recolectar, leerPagina: leerPagina, detener: function () { if (SOPORTADO && s.estado !== "inactivo") detener(); },
                     estado: function () { return { id: s.id, estado: s.estado }; } };
  pintar();
})();
