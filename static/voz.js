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
    noSoporta: "Tu navegador no permite escuchar respuestas. Puedes leerla en pantalla."
  };

  var s = { id: null, estado: "inactivo", mensaje: "", trozos: [], indice: 0, sesion: 0, voz: null };

  function grupos() { return document.querySelectorAll(".fc-voz"); }

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
    if (accion === "escuchar") escuchar(g.getAttribute("data-fc-voz-id"), g.getAttribute("data-fc-texto"));
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

  window.addEventListener("pagehide", function () { if (SOPORTADO) limpiar(); });

  window.__fcVoz = { pintar: pintar, estado: function () { return { id: s.id, estado: s.estado }; } };
  pintar();
})();
