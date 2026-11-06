/* Dictado por micrófono de Fuente Clara. Lo inserta modulos/voz.py dentro de cada botón "Dictar con el micrófono".
 *
 * - Usa el reconocimiento de voz del navegador (SpeechRecognition, es-CL). Fuente Clara no recibe ni guarda el audio.
 *   Ojo: en Chrome el navegador manda el audio al servicio de voz de Google para transcribirlo.
 * - La transcripción se escribe en el campo de texto de la persona, que la revisa y la corrige antes de enviar.
 * - Nunca escucha solo: parte de un clic o de Enter/Espacio sobre el botón, y se corta sola al terminar de hablar.
 * - Un único controlador por página: dictar en un campo detiene el dictado y la lectura en voz alta que hubiera.
 * - Sin llamadas de red propias, sin localStorage.
 */
(function () {
  "use strict";
  if (window.__fcDictado) { window.__fcDictado.pintar(); return; }

  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  var TEXTOS = {
    escuchando: "Escuchando… habla ahora.",
    procesando: "Procesando lo que dijiste…",
    listo: "Listo. Revisa el texto y corrígelo si hace falta.",
    sinVoz: "No te escuchamos. Intenta de nuevo, más cerca del micrófono.",
    permiso: "No tenemos permiso para usar el micrófono. Actívalo en los ajustes del navegador.",
    sinMicro: "No encontramos un micrófono en este dispositivo.",
    red: "No pudimos reconocer tu voz: el servicio de voz del navegador necesita conexión.",
    error: "No pudimos dictar. Puedes escribir tu texto a mano.",
    sinSoporte: "Tu navegador no permite dictar. Prueba con Chrome o escribe tu texto a mano.",
    inseguro: "El micrófono solo funciona en una conexión segura (HTTPS o localhost). Escribe tu texto a mano."
  };
  function motivoNoDisponible() {
    if (!SR) return TEXTOS.sinSoporte;
    if (window.isSecureContext === false) return TEXTOS.inseguro;
    return "";
  }

  var s = { rec: null, grupo: null, campo: null, base: "", estado: "inactivo", mensaje: "", sesion: 0 };

  function grupos() { return document.querySelectorAll(".fc-dictado"); }

  function pintar() {
    var bloqueo = motivoNoDisponible();
    grupos().forEach(function (g) {
      var propio = !bloqueo && g === s.grupo;
      var estado = propio ? s.estado : "inactivo";
      g.setAttribute("data-estado", estado);
      g.querySelectorAll("[data-fc-accion]").forEach(function (b) {
        var a = b.getAttribute("data-fc-accion");
        b.hidden = !((a === "dictar" && estado === "inactivo") || (a === "parar" && estado === "escuchando"));
        b.disabled = !!bloqueo;
      });
      var msg = g.querySelector(".fc-dictado-estado");
      if (msg) {
        var texto = bloqueo || (propio ? s.mensaje : "");
        if (msg.textContent !== texto) msg.textContent = texto;   // sin cambios no se toca el DOM
      }
    });
  }

  function campoDe(grupo) {
    var etiqueta = grupo.getAttribute("data-fc-destino");
    var campos = document.querySelectorAll("textarea");
    for (var i = 0; i < campos.length; i++) {
      if (campos[i].getAttribute("aria-label") === etiqueta) return campos[i];
    }
    return null;
  }

  function escribir(campo, valor) {
    var max = campo.maxLength > 0 ? campo.maxLength : 100000;
    var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
    setter.call(campo, valor.slice(0, max));
    campo.dispatchEvent(new Event("input", { bubbles: true }));   // así Streamlit se entera del cambio
  }

  function terminar(mensaje) {
    s.estado = "inactivo"; s.mensaje = mensaje;
    var campo = s.campo;
    pintar();
    if (campo && mensaje === TEXTOS.listo) campo.focus();          // para que la persona revise y corrija
  }

  function parar() {
    if (s.estado !== "escuchando" || !s.rec) return;
    s.estado = "procesando"; s.mensaje = TEXTOS.procesando;   // el navegador entrega lo último que oyó y llama a onend
    pintar();
    try { s.rec.stop(); } catch (e) { terminar(TEXTOS.error); }
  }

  function dictar(grupo) {
    if (motivoNoDisponible()) { pintar(); return; }
    var campo = campoDe(grupo);
    if (!campo) return;
    if (s.rec) { s.sesion++; try { s.rec.abort(); } catch (e) { /* nada */ } }
    // Mientras se dicta no debe sonar la lectura en voz alta (el micrófono la escucharía).
    if (window.__fcVoz && window.__fcVoz.detener) window.__fcVoz.detener();
    var sesion = ++s.sesion;
    var rec = new SR();
    rec.lang = "es-CL"; rec.interimResults = true; rec.continuous = false; rec.maxAlternatives = 1;
    s.rec = rec; s.grupo = grupo; s.campo = campo;
    s.base = campo.value.replace(/\s+$/, "");
    s.estado = "escuchando"; s.mensaje = TEXTOS.escuchando;
    var hubo = false;
    rec.onresult = function (e) {
      if (sesion !== s.sesion) return;
      var dicho = Array.prototype.map.call(e.results, function (r) { return r[0].transcript; }).join(" ").trim();
      if (!dicho) return;
      hubo = true;
      escribir(campo, (s.base ? s.base + " " : "") + dicho);
    };
    rec.onerror = function (e) {
      if (sesion !== s.sesion) return;
      var causa = e && e.error;
      if (causa === "aborted") return;
      var mensaje = TEXTOS.error;
      if (causa === "not-allowed" || causa === "service-not-allowed") mensaje = TEXTOS.permiso;
      else if (causa === "no-speech") mensaje = TEXTOS.sinVoz;
      else if (causa === "audio-capture") mensaje = TEXTOS.sinMicro;
      else if (causa === "network") mensaje = TEXTOS.red;
      s.sesion++;
      terminar(mensaje);
    };
    rec.onend = function () {
      if (sesion !== s.sesion) return;
      s.sesion++;
      terminar(hubo ? TEXTOS.listo : TEXTOS.sinVoz);
    };
    pintar();
    try { rec.start(); } catch (e) { s.sesion++; terminar(TEXTOS.error); }
  }

  function enfocarPrimero(grupo) {
    var b = grupo && grupo.querySelector("[data-fc-accion]:not([hidden])");
    if (b) b.focus();
  }

  document.addEventListener("click", function (ev) {
    var b = ev.target && ev.target.closest ? ev.target.closest(".fc-dictado [data-fc-accion]") : null;
    if (!b) return;
    var g = b.closest(".fc-dictado");
    var accion = b.getAttribute("data-fc-accion");
    if (accion === "dictar") dictar(g);
    else if (accion === "parar") parar();
    enfocarPrimero(g);   // el botón pulsado se oculta: el foco pasa al siguiente para no perder el teclado
  });

  // Si el campo desaparece (cambio de documento o de pestaña recargada), se corta el dictado.
  var revisando = null;
  new MutationObserver(function () {
    if (revisando) return;
    revisando = setTimeout(function () {
      revisando = null;
      if (s.estado === "escuchando" && !document.body.contains(s.campo)) {
        s.sesion++; try { s.rec.abort(); } catch (e) { /* nada */ }
        s.estado = "inactivo"; s.mensaje = "";
      }
      pintar();
    }, 500);
  }).observe(document.body, { childList: true, subtree: true });

  window.addEventListener("pagehide", function () { if (s.rec) { s.sesion++; try { s.rec.abort(); } catch (e) { /* nada */ } } });

  window.__fcDictado = { pintar: pintar, estado: function () { return s.estado; } };
  pintar();
})();
