/* Panel de accesibilidad de Fuente Clara (botón flotante con la figura de la persona). Lo inserta modulos/accesibilidad.py.
 *
 * - Tamaño de letra (80–200 %, de 10 en 10): cambia solo la variable --fc-escala-texto; static/estilo.css la usa en los
 *   font-size de los textos. No hay zoom, transform ni cambios al ancho de la página, las tarjetas, las imágenes ni los íconos.
 * - Alto contraste: el control va de 0 a 100 %. Mientras no llega al 100 % la página conserva su paleta original; en 100 %
 *   se activa la paleta de alto contraste (html[data-fc-contraste="alto"]). No hay filtros ni interruptor aparte.
 * - Lectura por voz: botones de la página completa (los maneja static/voz.js, que comparte el estado con los botones
 *   «Escuchar respuesta», así nunca suenan dos a la vez).
 * - Se guardan solo el tamaño y el contraste (localStorage). Nunca audio ni textos. La lectura jamás empieza sola.
 */
(function () {
  "use strict";
  if (window.__fcAcc) return;

  var LLAVE = "fc_preferencias_accesibilidad_v3";
  var TAMANO = { min: 80, max: 200, paso: 10, inicial: 100 };
  var ID_LECTOR = "__LECTOR__";
  var raiz = document.documentElement;

  var ICONO = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="4" r="2.2"/>' +
    '<path d="M19 13v-2c-1.54.02-3.09-.75-4.07-1.83l-1.29-1.43c-.17-.19-.38-.34-.61-.45-.48-.23-1.07-.23-1.55.01-.24.11-.45.27-.63.47l-1.3 1.44' +
    'C8.56 10.27 7.02 11.02 5.5 11v2c2.01 0 3.84-.94 5-2.43V14l-3.4 6H9.3l2.7-4.76L14.7 20h2.2l-3.4-6v-3.43c1.16 1.49 2.99 2.43 5 2.43z"/></svg>';

  function botonVoz(accion, etiqueta, descripcion, oculto) {
    return '<button type="button" data-fc-accion="' + accion + '" aria-label="' + descripcion + '"' + (oculto ? " hidden" : "") +
      "><span>" + etiqueta + "</span></button>";
  }

  var host = document.createElement("div");
  host.id = "fc-accesibilidad-host";
  host.innerHTML =
    '<button type="button" id="fc-btn-flotante-acc" class="fc-acc-flotante" aria-label="Abrir opciones de accesibilidad" ' +
    'aria-haspopup="dialog" aria-expanded="false" title="Accesibilidad">' + ICONO + "</button>" +
    '<div id="fc-panel-acc-fondo" class="fc-acc-fondo"></div>' +
    '<section id="fc-panel-acc" class="fc-acc-panel" role="dialog" aria-modal="true" aria-labelledby="fc-titulo-acc" aria-hidden="true">' +
      '<div class="fc-acc-cabecera"><h2 id="fc-titulo-acc" class="fc-acc-titulo">' + ICONO + " Accesibilidad</h2>" +
      '<button type="button" id="fc-btn-cerrar-acc" class="fc-acc-cerrar" aria-label="Cerrar el panel de accesibilidad">✕</button></div>' +

      '<div class="fc-acc-bloque">' +
        '<div class="fc-acc-fila"><label for="fc-slider-tamano" class="fc-acc-nombre">Tamaño de letra</label>' +
        '<span id="fc-valor-tamano" class="fc-acc-valor">100%</span></div>' +
        '<input type="range" id="fc-slider-tamano" class="fc-acc-deslizador" min="' + TAMANO.min + '" max="' + TAMANO.max + '" step="' + TAMANO.paso +
        '" value="' + TAMANO.inicial + '" aria-valuetext="100 por ciento">' +
        '<div class="fc-acc-marcas" aria-hidden="true"><span>80%</span><span>100%</span><span>200%</span></div>' +
        '<p class="fc-acc-ayuda">Cambia solo el tamaño de las letras. En 100% vuelve al tamaño original.</p>' +
      "</div>" +

      '<div class="fc-acc-bloque">' +
        '<div class="fc-acc-fila"><label for="fc-slider-contraste" class="fc-acc-nombre">Alto contraste</label>' +
        '<span id="fc-valor-contraste" class="fc-acc-valor">0%</span></div>' +
        '<input type="range" id="fc-slider-contraste" class="fc-acc-deslizador" min="0" max="100" step="1" value="0" aria-valuetext="0 por ciento, colores originales" aria-describedby="fc-ayuda-contraste">' +
        '<div class="fc-acc-marcas" aria-hidden="true"><span>Original</span><span>Alto contraste</span></div>' +
        '<p id="fc-ayuda-contraste" class="fc-acc-ayuda" role="status" aria-live="polite">Lleva el control hasta el 100% (tecla Fin) para activar el alto contraste.</p>' +
      "</div>" +

      '<div class="fc-acc-bloque" role="group" aria-labelledby="fc-nombre-voz">' +
        '<div class="fc-acc-fila"><span id="fc-nombre-voz" class="fc-acc-nombre">Lectura por voz</span></div>' +
        '<div class="fc-voz" role="group" aria-label="Lectura de la página completa" data-estado="inactivo" data-fc-voz-id="' + ID_LECTOR + '" data-fc-pagina="1">' +
          '<div class="fc-voz-botones">' +
            botonVoz("escuchar", "Leer página completa", "Leer la página completa en voz alta", false) +
            botonVoz("pausar", "Pausar", "Pausar la lectura", true) +
            botonVoz("continuar", "Continuar", "Continuar la lectura", true) +
            botonVoz("detener", "Detener", "Detener la lectura", true) +
          "</div>" +
          '<span class="fc-voz-estado" role="status" aria-live="polite"></span>' +
        "</div>" +
        '<p class="fc-acc-ayuda">Lee el título, las explicaciones, las respuestas y las citas de la pestaña que estás viendo.</p>' +
      "</div>" +

      '<button type="button" id="fc-btn-reset-acc" class="fc-acc-restablecer">Restablecer preferencias</button>' +
    "</section>";
  document.body.appendChild(host);

  var botonFlotante = document.getElementById("fc-btn-flotante-acc");
  var panel = document.getElementById("fc-panel-acc");
  var fondo = document.getElementById("fc-panel-acc-fondo");
  var cerrar = document.getElementById("fc-btn-cerrar-acc");
  var reset = document.getElementById("fc-btn-reset-acc");
  var sTamano = document.getElementById("fc-slider-tamano");
  var vTamano = document.getElementById("fc-valor-tamano");
  var sContraste = document.getElementById("fc-slider-contraste");
  var vContraste = document.getElementById("fc-valor-contraste");
  var ayudaContraste = document.getElementById("fc-ayuda-contraste");

  function acotar(v, min, max, defecto) {
    v = Number(v);
    return isFinite(v) ? Math.max(min, Math.min(max, v)) : defecto;
  }

  function guardar() {
    try {
      localStorage.setItem(LLAVE, JSON.stringify({ tamano: Number(sTamano.value), contraste: Number(sContraste.value) }));
    } catch (e) { /* sin almacenamiento: las preferencias valen solo en esta visita */ }
  }

  function cargar() {
    try { return JSON.parse(localStorage.getItem(LLAVE) || "null"); } catch (e) { return null; }
  }

  function aplicarTamano(v) {
    v = Math.round(acotar(v, TAMANO.min, TAMANO.max, TAMANO.inicial) / TAMANO.paso) * TAMANO.paso;
    sTamano.value = v;
    vTamano.textContent = v + "%";
    sTamano.setAttribute("aria-valuetext", v + " por ciento" + (v === 100 ? ", tamaño original" : ""));
    if (v === TAMANO.inicial) raiz.style.removeProperty("--fc-escala-texto");   // 100 %: vuelve exactamente al original
    else raiz.style.setProperty("--fc-escala-texto", String(v / 100));
  }

  function aplicarContraste(v) {
    v = Math.round(acotar(v, 0, 100, 0));
    sContraste.value = v;
    vContraste.textContent = v + "%";
    var alto = v >= 100;                    // solo en 100 % cambia la paleta; de 0 a 99 % solo avanza el control
    if (alto) raiz.setAttribute("data-fc-contraste", "alto"); else raiz.removeAttribute("data-fc-contraste");
    sContraste.setAttribute("aria-valuetext", alto ? "100 por ciento, alto contraste activado" : v + " por ciento, colores originales");
    ayudaContraste.textContent = alto ? "Alto contraste activado." : "Lleva el control hasta el 100% (tecla Fin) para activar el alto contraste.";
  }

  sTamano.addEventListener("input", function () { aplicarTamano(sTamano.value); guardar(); });
  sContraste.addEventListener("input", function () { aplicarContraste(sContraste.value); guardar(); });
  reset.addEventListener("click", function () {
    aplicarTamano(TAMANO.inicial); aplicarContraste(0); guardar();
    ayudaContraste.textContent = "Preferencias restablecidas: tamaño y colores originales.";
  });

  function abrir() {
    panel.classList.add("fc-visible"); fondo.classList.add("fc-visible");
    panel.setAttribute("aria-hidden", "false"); botonFlotante.setAttribute("aria-expanded", "true");
    cerrar.focus();
  }
  function cerrarPanel() {
    panel.classList.remove("fc-visible"); fondo.classList.remove("fc-visible");
    panel.setAttribute("aria-hidden", "true"); botonFlotante.setAttribute("aria-expanded", "false");
    botonFlotante.focus();
  }
  botonFlotante.addEventListener("click", abrir);
  cerrar.addEventListener("click", cerrarPanel);
  fondo.addEventListener("click", cerrarPanel);

  document.addEventListener("keydown", function (ev) {
    if (!panel.classList.contains("fc-visible")) return;
    if (ev.key === "Escape") { cerrarPanel(); return; }
    if (ev.key !== "Tab") return;
    // El foco queda dentro del diálogo mientras está abierto.
    var items = Array.prototype.filter.call(panel.querySelectorAll("button, input"), function (n) { return !n.hidden && !n.disabled; });
    if (!items.length) return;
    var primero = items[0], ultimo = items[items.length - 1];
    if (ev.shiftKey && document.activeElement === primero) { ultimo.focus(); ev.preventDefault(); }
    else if (!ev.shiftKey && document.activeElement === ultimo) { primero.focus(); ev.preventDefault(); }
  });

  // Preferencias guardadas (solo tamaño y contraste). La lectura nunca arranca sola al recargar.
  var pref = cargar() || {};
  aplicarTamano(pref.tamano === undefined ? TAMANO.inicial : pref.tamano);
  aplicarContraste(pref.contraste === undefined ? 0 : pref.contraste);

  window.__fcAcc = { tamano: function () { return Number(sTamano.value); }, contraste: function () { return Number(sContraste.value); } };
  if (window.__fcVoz) window.__fcVoz.pintar();
})();
