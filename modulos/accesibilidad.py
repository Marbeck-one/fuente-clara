"""Módulo de accesibilidad adaptativa · Fuente Clara.

Implementa el sistema de accesibilidad visual conforme a WCAG 2.2:
1. Contraste adaptativo continuo (slider 0 a 100) sin alterar fotos/documentos,
   conservando la identidad visual institucional de Fuente Clara.
2. Tamaño de letra proporcional (slider 50% a 150%) sin desbordamientos.
3. Espaciado de lectura adaptable (slider 100% a 150%) para interlineado y separación de caracteres.
4. Botón flotante accesible centrado en el borde derecho con la figura universal de la persona.
5. Persistencia automática en localStorage y restablecimiento de configuración.
6. Cierre con tecla Escape y soporte de teclado accesible.

Tokens y criterios de diseño en DESIGN.md §3, §5 y §9.
"""
import streamlit as st
import streamlit.components.v1 as components

# Paletas institucionales calibradas bajo WCAG 2.2
PALETAS_WCAG = {
    "normal": {
        "fondo": "#F8FAFC",
        "superficie": "#FFFFFF",
        "campo": "#F1F5F9",
        "borde": "#CBD5E1",
        "tinta": "#083344",
        "tinta_hover": "#164E63",
        "texto": "#0F172A",
        "texto2": "#334155",
        "texto3": "#475569",
        "accion": "#0E7490",
        "resaltador": "#FDE68A",
        "resaltador_texto": "#0F172A",
    },
    "intermedio": {
        "fondo": "#EDF2F7",
        "superficie": "#FFFFFF",
        "campo": "#E2E8F0",
        "borde": "#64748B",
        "tinta": "#03202B",
        "tinta_hover": "#0C2F3D",
        "texto": "#020617",
        "texto2": "#1E293B",
        "texto3": "#334155",
        "accion": "#0369A1",
        "resaltador": "#FDE047",
        "resaltador_texto": "#020617",
    },
    "alto": {
        "fondo": "#041319",
        "superficie": "#08202A",
        "campo": "#0E2E3C",
        "borde": "#38BDF8",
        "tinta": "#F8FAFC",
        "tinta_hover": "#E2E8F0",
        "texto": "#FFFFFF",
        "texto2": "#E2E8F0",
        "texto3": "#94A3B8",
        "accion": "#38BDF8",
        "resaltador": "#FACC15",
        "resaltador_texto": "#041319",
    },
}


HTML_ACCESIBILIDAD_COMPONENTE = """
<script>
(function() {
  const pDoc = window.parent.document;
  if (!pDoc) return;

  // Evitar duplicar el panel si ya existe en el DOM
  if (pDoc.getElementById('fc-accesibilidad-host')) return;

  const host = pDoc.createElement('div');
  host.id = 'fc-accesibilidad-host';
  pDoc.body.appendChild(host);

  // Paletas calibradas para interpolación continua (0 a 100)
  const PALETA_NORMAL = {
    fondo: [248, 250, 252],       // #F8FAFC
    superficie: [255, 255, 255],  // #FFFFFF
    campo: [241, 245, 249],       // #F1F5F9
    borde: [203, 213, 225],       // #CBD5E1
    tinta: [8, 51, 68],           // #083344
    tintaHover: [22, 78, 99],     // #164E63
    texto: [15, 23, 42],          // #0F172A
    texto2: [51, 65, 85],         // #334155
    texto3: [71, 85, 105],        // #475569
    accion: [14, 116, 144],       // #0E7490
    resaltador: [253, 230, 138],  // #FDE68A
    resaltadorTexto: [15, 23, 42] // #0F172A
  };

  const PALETA_INTERMEDIO = {
    fondo: [237, 242, 247],       // #EDF2F7
    superficie: [255, 255, 255],  // #FFFFFF
    campo: [226, 232, 240],       // #E2E8F0
    borde: [100, 116, 139],       // #64748B
    tinta: [3, 32, 43],           // #03202B
    tintaHover: [12, 47, 61],     // #0C2F3D
    texto: [2, 6, 23],            // #020617
    texto2: [30, 41, 59],         // #1E293B
    texto3: [51, 65, 85],         // #334155
    accion: [3, 105, 161],        // #0369A1
    resaltador: [253, 224, 71],   // #FDE047
    resaltadorTexto: [2, 6, 23]   // #020617
  };

  const PALETA_ALTO = {
    fondo: [4, 19, 25],           // #041319 (Petróleo oscuro profundo)
    superficie: [8, 32, 42],      // #08202A (Superficie institucional oscura)
    campo: [14, 46, 60],          // #0E2E3C
    borde: [56, 189, 248],        // #38BDF8 (Cian nítido)
    tinta: [248, 250, 252],       // #F8FAFC
    tintaHover: [226, 232, 240],  // #E2E8F0
    texto: [255, 255, 255],       // #FFFFFF (Blanco puro nítido)
    texto2: [226, 232, 240],      // #E2E8F0
    texto3: [148, 163, 184],      // #94A3B8
    accion: [56, 189, 248],       // #38BDF8
    resaltador: [250, 204, 21],   // #FACC15
    resaltadorTexto: [4, 19, 25]  // #041319
  };

  function lerp(a, b, t) {
    return Math.round(a + (b - a) * t);
  }

  function lerpColor(c1, c2, t) {
    const r = lerp(c1[0], c2[0], t);
    const g = lerp(c1[1], c2[1], t);
    const b = lerp(c1[2], c2[2], t);
    return `rgb(${r}, ${g}, ${b})`;
  }

  function aplicarContraste(nivel) {
    nivel = Math.max(0, Math.min(100, Number(nivel)));
    const root = pDoc.documentElement;
    let t, cA, cB;

    if (nivel <= 50) {
      t = nivel / 50;
      cA = PALETA_NORMAL;
      cB = PALETA_INTERMEDIO;
    } else {
      t = (nivel - 50) / 50;
      cA = PALETA_INTERMEDIO;
      cB = PALETA_ALTO;
    }

    root.style.setProperty('--fc-fondo', lerpColor(cA.fondo, cB.fondo, t));
    root.style.setProperty('--fc-superficie', lerpColor(cA.superficie, cB.superficie, t));
    root.style.setProperty('--fc-campo', lerpColor(cA.campo, cB.campo, t));
    root.style.setProperty('--fc-borde', lerpColor(cA.borde, cB.borde, t));
    root.style.setProperty('--fc-tinta', lerpColor(cA.tinta, cB.tinta, t));
    root.style.setProperty('--fc-tinta-hover', lerpColor(cA.tintaHover, cB.tintaHover, t));
    root.style.setProperty('--fc-texto', lerpColor(cA.texto, cB.texto, t));
    root.style.setProperty('--fc-texto-2', lerpColor(cA.texto2, cB.texto2, t));
    root.style.setProperty('--fc-texto-3', lerpColor(cA.texto3, cB.texto3, t));
    root.style.setProperty('--fc-accion', lerpColor(cA.accion, cB.accion, t));
    root.style.setProperty('--fc-resaltador', lerpColor(cA.resaltador, cB.resaltador, t));
    root.style.setProperty('--fc-resaltador-texto', lerpColor(cA.resaltadorTexto, cB.resaltadorTexto, t));

    // Si el contraste supera el 50%, aplicar clase para sombras e indicadores
    if (nivel > 50) {
      root.classList.add('fc-modo-oscuro-contraste');
    } else {
      root.classList.remove('fc-modo-oscuro-contraste');
    }
  }

  function aplicarTamano(tam) {
    tam = Math.max(50, Math.min(150, Number(tam)));
    const escala = tam / 100;
    pDoc.documentElement.style.setProperty('--fc-font-scale', escala);
  }

  function aplicarEspaciado(esp) {
    esp = Math.max(100, Math.min(150, Number(esp)));
    const escalaInterlineado = esp / 100;
    const tracking = (esp - 100) * 0.0016; // de 0em a 0.08em
    pDoc.documentElement.style.setProperty('--fc-line-height-scale', escalaInterlineado);
    pDoc.documentElement.style.setProperty('--fc-letter-spacing', `${tracking}em`);
  }

  // Estructura visual del botón flotante y el panel
  host.innerHTML = `
    <style id="fc-estilos-host-accesibilidad">
      /* Botón flotante centrado en el borde derecho */
      #fc-btn-flotante-acc {
        position: fixed !important;
        right: 0 !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 999999 !important;
        width: 48px !important;
        height: 52px !important;
        border-radius: 26px 0 0 26px !important;
        background-color: var(--fc-tinta, #083344) !important;
        color: #FFFFFF !important;
        border: 2px solid var(--fc-superficie, #FFFFFF) !important;
        border-right: none !important;
        box-shadow: -3px 4px 16px rgba(8, 51, 68, 0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        padding-left: 6px !important;
        padding-right: 0 !important;
        transition: transform 0.2s ease, background-color 0.2s ease, width 0.2s ease !important;
        outline: none !important;
      }
      #fc-btn-flotante-acc:hover, #fc-btn-flotante-acc:focus-visible {
        width: 54px !important;
        background-color: var(--fc-tinta-hover, #164E63) !important;
        outline: 2px solid var(--fc-accion, #0E7490) !important;
        outline-offset: 2px !important;
      }
      #fc-btn-flotante-acc svg {
        width: 26px !important;
        height: 26px !important;
        fill: #FFFFFF !important;
      }

      /* Backdrop sutil */
      #fc-panel-acc-backdrop {
        position: fixed !important;
        inset: 0 !important;
        background: rgba(15, 23, 42, 0.3) !important;
        backdrop-filter: blur(2px) !important;
        z-index: 1000000 !important;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.25s ease !important;
      }
      #fc-panel-acc-backdrop.fc-visible {
        opacity: 1 !important;
        pointer-events: auto !important;
      }

      /* Panel deslizable de opciones de accesibilidad */
      #fc-panel-acc {
        position: fixed !important;
        right: 1rem !important;
        top: 50% !important;
        transform: translateY(-50%) scale(0.95) !important;
        width: 340px !important;
        max-width: calc(100vw - 2rem) !important;
        max-height: 90vh !important;
        background: var(--fc-superficie, #FFFFFF) !important;
        color: var(--fc-texto, #0F172A) !important;
        border: 1px solid var(--fc-borde, #CBD5E1) !important;
        border-radius: 1rem !important;
        box-shadow: 0 20px 40px rgba(15, 23, 42, 0.2) !important;
        z-index: 1000001 !important;
        padding: 1.25rem !important;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1), transform 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        overflow-y: auto !important;
        box-sizing: border-box !important;
        font-family: 'Atkinson Hyperlegible Next', system-ui, sans-serif !important;
      }
      #fc-panel-acc.fc-visible {
        opacity: 1 !important;
        pointer-events: auto !important;
        transform: translateY(-50%) scale(1) !important;
      }

      .fc-pnl-header {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        border-bottom: 1px solid var(--fc-borde, #E2E8F0) !important;
        padding-bottom: .75rem !important;
        margin-bottom: 1rem !important;
      }
      .fc-pnl-header-title {
        display: flex !important;
        align-items: center !important;
        gap: .5rem !important;
        font-size: 1.0625rem !important;
        font-weight: 800 !important;
        color: var(--fc-tinta, #083344) !important;
        margin: 0 !important;
      }
      .fc-pnl-header-title svg {
        width: 20px !important;
        height: 20px !important;
        fill: var(--fc-tinta, #083344) !important;
      }
      .fc-pnl-close {
        background: none !important;
        border: none !important;
        font-size: 1.25rem !important;
        cursor: pointer !important;
        color: var(--fc-texto-2, #475569) !important;
        padding: .25rem .5rem !important;
        border-radius: .375rem !important;
        line-height: 1 !important;
      }
      .fc-pnl-close:hover, .fc-pnl-close:focus-visible {
        background: var(--fc-campo, #F1F5F9) !important;
        color: var(--fc-tinta, #083344) !important;
        outline: 2px solid var(--fc-accion, #0E7490) !important;
      }

      /* Control item */
      .fc-ctrl-item {
        margin-bottom: 1.125rem !important;
      }
      .fc-ctrl-label-row {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: .375rem !important;
      }
      .fc-ctrl-name {
        font-size: .8125rem !important;
        font-weight: 700 !important;
        letter-spacing: .08em !important;
        text-transform: uppercase !important;
        color: var(--fc-accion, #0E7490) !important;
      }
      .fc-ctrl-badge {
        font-size: .8125rem !important;
        font-weight: 700 !important;
        background: var(--fc-campo, #F1F5F9) !important;
        color: var(--fc-tinta, #083344) !important;
        padding: .15rem .5rem !important;
        border-radius: 999px !important;
        border: 1px solid var(--fc-borde, #CBD5E1) !important;
      }

      /* Sliders accesibles */
      .fc-slider {
        width: 100% !important;
        height: 8px !important;
        border-radius: 4px !important;
        background: var(--fc-campo, #E2E8F0) !important;
        outline: none !important;
        cursor: pointer !important;
        accent-color: var(--fc-tinta, #083344) !important;
        margin: .375rem 0 !important;
      }
      .fc-slider:focus-visible {
        outline: 2px solid var(--fc-accion, #0E7490) !important;
        outline-offset: 4px !important;
      }
      .fc-slider-ticks {
        display: flex !important;
        justify-content: space-between !important;
        font-size: .6875rem !important;
        color: var(--fc-texto-3, #64748B) !important;
        font-weight: 600 !important;
      }

      /* Botón restablecer */
      .fc-btn-reset {
        width: 100% !important;
        min-height: 42px !important;
        border-radius: .5rem !important;
        border: 1px solid var(--fc-borde, #CBD5E1) !important;
        background: var(--fc-campo, #F1F5F9) !important;
        color: var(--fc-tinta, #083344) !important;
        font-weight: 700 !important;
        font-size: .875rem !important;
        cursor: pointer !important;
        margin-top: .5rem !important;
        transition: background-color 0.15s ease, border-color 0.15s ease !important;
      }
      .fc-btn-reset:hover, .fc-btn-reset:focus-visible {
        background: var(--fc-borde, #E2E8F0) !important;
        border-color: var(--fc-tinta, #083344) !important;
        outline: 2px solid var(--fc-accion, #0E7490) !important;
      }
    </style>

    <!-- Botón flotante accesible (centro derecho) -->
    <button id="fc-btn-flotante-acc" aria-label="Abrir opciones de accesibilidad visual" title="Opciones de accesibilidad">
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <circle cx="12" cy="4" r="2.2"/>
        <path d="M19 13v-2c-1.54.02-3.09-.75-4.07-1.83l-1.29-1.43c-.17-.19-.38-.34-.61-.45-.48-.23-1.07-.23-1.55.01-.24.11-.45.27-.63.47l-1.3 1.44C8.56 10.27 7.02 11.02 5.5 11v2c2.01 0 3.84-.94 5-2.43V14l-3.4 6H9.3l2.7-4.76L14.7 20h2.2l-3.4-6v-3.43c1.16 1.49 2.99 2.43 5 2.43z"/>
      </svg>
    </button>

    <!-- Backdrop -->
    <div id="fc-panel-acc-backdrop"></div>

    <!-- Panel flotante -->
    <section id="fc-panel-acc" role="dialog" aria-modal="true" aria-labelledby="fc-titulo-acc" aria-hidden="true">
      <div class="fc-pnl-header">
        <h2 id="fc-titulo-acc" class="fc-pnl-header-title">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="4" r="2.2"/>
            <path d="M19 13v-2c-1.54.02-3.09-.75-4.07-1.83l-1.29-1.43c-.17-.19-.38-.34-.61-.45-.48-.23-1.07-.23-1.55.01-.24.11-.45.27-.63.47l-1.3 1.44C8.56 10.27 7.02 11.02 5.5 11v2c2.01 0 3.84-.94 5-2.43V14l-3.4 6H9.3l2.7-4.76L14.7 20h2.2l-3.4-6v-3.43c1.16 1.49 2.99 2.43 5 2.43z"/>
          </svg>
          Accesibilidad
        </h2>
        <button id="fc-btn-cerrar-acc" class="fc-pnl-close" aria-label="Cerrar panel de accesibilidad">✕</button>
      </div>

      <!-- Control 1: Contraste Progresivo (0 - 100) -->
      <div class="fc-ctrl-item">
        <div class="fc-ctrl-label-row">
          <label for="fc-slider-contraste" class="fc-ctrl-name">Contraste</label>
          <span id="fc-badge-contraste" class="fc-ctrl-badge">0% Normal</span>
        </div>
        <input type="range" id="fc-slider-contraste" class="fc-slider" min="0" max="100" step="1" value="0" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" aria-label="Nivel de contraste progresivo">
        <div class="fc-slider-ticks">
          <span>Normal (0%)</span>
          <span>Intermedio (50%)</span>
          <span>Alto (100%)</span>
        </div>
      </div>

      <!-- Control 2: Tamaño de letra (50% - 150%) -->
      <div class="fc-ctrl-item">
        <div class="fc-ctrl-label-row">
          <label for="fc-slider-tamano" class="fc-ctrl-name">Tamaño de letra</label>
          <span id="fc-badge-tamano" class="fc-ctrl-badge">100%</span>
        </div>
        <input type="range" id="fc-slider-tamano" class="fc-slider" min="50" max="150" step="5" value="100" aria-valuemin="50" aria-valuemax="150" aria-valuenow="100" aria-label="Tamaño proporcional de letra">
        <div class="fc-slider-ticks">
          <span>50%</span>
          <span>100% (Normal)</span>
          <span>150%</span>
        </div>
      </div>

      <!-- Control 3: Espaciado de lectura (100% - 150%) -->
      <div class="fc-ctrl-item">
        <div class="fc-ctrl-label-row">
          <label for="fc-slider-espaciado" class="fc-ctrl-name">Espaciado</label>
          <span id="fc-badge-espaciado" class="fc-ctrl-badge">Normal</span>
        </div>
        <input type="range" id="fc-slider-espaciado" class="fc-slider" min="100" max="150" step="5" value="100" aria-valuemin="100" aria-valuemax="150" aria-valuenow="100" aria-label="Espaciado entre líneas y caracteres">
        <div class="fc-slider-ticks">
          <span>Normal</span>
          <span>Amplio</span>
          <span>Máximo</span>
        </div>
      </div>

      <!-- Botón Restablecer -->
      <button id="fc-btn-reset-acc" class="fc-btn-reset">Restablecer valores originales</button>
    </section>
  `;

  // Referencias a elementos
  const btnFlotante = pDoc.getElementById('fc-btn-flotante-acc');
  const panel = pDoc.getElementById('fc-panel-acc');
  const backdrop = pDoc.getElementById('fc-panel-acc-backdrop');
  const btnCerrar = pDoc.getElementById('fc-btn-cerrar-acc');
  const btnReset = pDoc.getElementById('fc-btn-reset-acc');

  const sldContraste = pDoc.getElementById('fc-slider-contraste');
  const badgeContraste = pDoc.getElementById('fc-badge-contraste');
  const sldTamano = pDoc.getElementById('fc-slider-tamano');
  const badgeTamano = pDoc.getElementById('fc-badge-tamano');
  const sldEspaciado = pDoc.getElementById('fc-slider-espaciado');
  const badgeEspaciado = pDoc.getElementById('fc-badge-espaciado');

  const STORAGE_KEY = 'fc_preferencias_accesibilidad_v2';

  function guardarPreferencias(config) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
    } catch(e) {}
  }

  function cargarPreferencias() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : null;
    } catch(e) {
      return null;
    }
  }

  function actualizarBadgeContraste(v) {
    v = Number(v);
    if (v === 0) badgeContraste.textContent = '0% Normal';
    else if (v < 50) badgeContraste.textContent = `${v}% Suave`;
    else if (v === 50) badgeContraste.textContent = '50% Intermedio';
    else if (v < 100) badgeContraste.textContent = `${v}% Alto`;
    else badgeContraste.textContent = '100% Máximo';
  }

  function actualizarBadgeEspaciado(v) {
    v = Number(v);
    if (v <= 105) badgeEspaciado.textContent = 'Normal';
    else if (v <= 125) badgeEspaciado.textContent = 'Amplio';
    else badgeEspaciado.textContent = 'Máximo';
  }

  function aplicarTodo(contraste, tamano, espaciado) {
    sldContraste.value = contraste;
    sldContraste.setAttribute('aria-valuenow', contraste);
    actualizarBadgeContraste(contraste);
    aplicarContraste(contraste);

    sldTamano.value = tamano;
    sldTamano.setAttribute('aria-valuenow', tamano);
    badgeTamano.textContent = `${tamano}%`;
    aplicarTamano(tamano);

    sldEspaciado.value = espaciado;
    sldEspaciado.setAttribute('aria-valuenow', espaciado);
    actualizarBadgeEspaciado(espaciado);
    aplicarEspaciado(espaciado);

    guardarPreferencias({ contraste, tamano, espaciado });
  }

  function abrirPanel() {
    panel.classList.add('fc-visible');
    backdrop.classList.add('fc-visible');
    panel.setAttribute('aria-hidden', 'false');
    btnCerrar.focus();
  }

  function cerrarPanel() {
    panel.classList.remove('fc-visible');
    backdrop.classList.remove('fc-visible');
    panel.setAttribute('aria-hidden', 'true');
    btnFlotante.focus();
  }

  // Event Listeners interactivos e inmediatos (0 ms)
  sldContraste.addEventListener('input', (e) => {
    const val = Number(e.target.value);
    actualizarBadgeContraste(val);
    aplicarContraste(val);
    guardarPreferencias({
      contraste: val,
      tamano: Number(sldTamano.value),
      espaciado: Number(sldEspaciado.value)
    });
  });

  sldTamano.addEventListener('input', (e) => {
    const val = Number(e.target.value);
    badgeTamano.textContent = `${val}%`;
    aplicarTamano(val);
    guardarPreferencias({
      contraste: Number(sldContraste.value),
      tamano: val,
      espaciado: Number(sldEspaciado.value)
    });
  });

  sldEspaciado.addEventListener('input', (e) => {
    const val = Number(e.target.value);
    actualizarBadgeEspaciado(val);
    aplicarEspaciado(val);
    guardarPreferencias({
      contraste: Number(sldContraste.value),
      tamano: Number(sldTamano.value),
      espaciado: val
    });
  });

  btnReset.addEventListener('click', () => {
    aplicarTodo(0, 100, 100);
  });

  btnFlotante.addEventListener('click', abrirPanel);
  btnCerrar.addEventListener('click', cerrarPanel);
  backdrop.addEventListener('click', cerrarPanel);

  // Accesibilidad con teclado: Cerrar con Escape
  pDoc.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && panel.classList.contains('fc-visible')) {
      cerrarPanel();
    }
  });

  // Restaurar preferencias guardadas en localStorage
  const pref = cargarPreferencias();
  if (pref) {
    aplicarTodo(pref.contraste ?? 0, pref.tamano ?? 100, pref.espaciado ?? 100);
  } else {
    aplicarTodo(0, 100, 100);
  }
})();
</script>
"""


def render_panel():
    """Monta el acceso flotante y el sistema interactivo de contraste adaptativo."""
    components.html(HTML_ACCESIBILIDAD_COMPONENTE, height=0, width=0)


# Alias para app.py
render_interruptor = render_panel
