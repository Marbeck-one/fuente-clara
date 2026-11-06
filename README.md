# Fuente Clara

*Entender, verificar, preguntar.* Prototipo para el Desafío 3 (Democracia) de la Hackathon de IA Aplicada · Congreso Social UC 2026.

Trabaja **solo** sobre un documento público oficial precargado (un proyecto de ley) con tres módulos:

1. **Explícame:** responde en lenguaje claro, con citas verificadas del artículo exacto.
2. **Verifica esto:** pone lado a lado una cadena o post y lo que dice el texto oficial, sin veredictos. También puede leer el texto de una captura de pantalla.
3. **Pregúntale al Estado:** si el documento no responde la duda, prepara un borrador de solicitud de transparencia que la persona revisa y envía por su cuenta.

## Instalación

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuración (.env)

```bash
cp .env.example .env      # en Windows: copy .env.example .env
```

Completa en `.env`:

- `LLM_PROVIDER`: `anthropic`, `openai` o `google`.
- `LLM_MODEL`: nombre exacto del modelo disponible en tu cuenta.
- La clave del proveedor elegido (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY` o `GOOGLE_API_KEY`).

Antes de la demo, revisa que todo esté configurado sin gastar tokens:

```bash
python scripts/verificar_entorno.py
```

Con `--probar` hace además una llamada mínima real al modelo.

## Ejecutar

```bash
streamlit run app.py
```

Para verlo en el celular, abre la "Network URL" que muestra Streamlit (mismo wifi).

## Evaluar

```bash
python scripts/evaluar.py
```

Corre `tests/preguntas_prueba.json` contra los tres módulos, igual que la app (filtro y guardrail incluidos), y al final imprime una tabla en Markdown lista para el pitch y `DECLARACION_IA.md`:

- **Explícame:** % de respuestas con cita verificada, de preguntas sin el dato o de otro tema detectadas, y de tendenciosas e intentos de manipulación rechazados.
- **Verifica esto:** % de afirmaciones con la etiqueta esperada.
- **Pregúntale al Estado:** el organismo sugerido para cada pregunta sin el dato. Una persona marca si es razonable.
- **Tiempo promedio de respuesta** por módulo, sin contar la espera de `LLM_INTERVALO_MIN`.
- **Votos 👍/👎** de la app con ese documento y ese modelo.

Con APIs gratuitas, que son lentas, se puede correr por partes: `--modulo explicame|verifica|estado` o `--tipo normal|fuera|otro_tema|tendenciosa|manipulacion` (solo Explícame).

Para evaluar las afirmaciones de «Verifica esto»:

```bash
python scripts/evaluar.py --verifica
```

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q                 # no usa la API ni necesita .env
python scripts/smoke.py   # documento, citas, guardrail y configuración legal
```

Prueba de integración real de los tres módulos (consume la API y requiere `.env`):

```bash
python scripts/probar_app.py
```

Prueba real de lectura de capturas en «Verifica esto» (genera la imagen en memoria, no la guarda,
y consume unas 5 solicitudes):

```bash
python scripts/probar_imagen.py
```

La imagen no se guarda en disco ni en los votos. En la app, el texto extraído se puede corregir
antes de comparar. No subas capturas con nombres, teléfonos, RUT u otros datos personales.

## Calidad de las respuestas (votos)

Bajo cada respuesta la persona vota 👍 o 👎. Los votos se guardan en `data/votos/votos.jsonl` (fuera del repo) con el modelo y la versión de las instrucciones. El enlace «Cómo nos va», al final de la app, abre el panel con los resultados. Para ver las respuestas que las personas autorizaron guardar, define `CLAVE_EQUIPO` en `.env`.

## Cuenta opcional

Por defecto no hay login y la app funciona como siempre. Si se activa, cualquiera sigue usando todo sin cuenta; lo único que cambia es el tope: **5 consultas cada 10 minutos sin cuenta y 20 con cuenta** (el tope global de 30 por minuto no cambia, así que el gasto máximo de la API tampoco). Módulos, citas, voz y accesibilidad nunca dependen de la cuenta.

- **Modo demostración (`AUTH_MOCK=1` en `.env`):** simula el login sin contactar a ningún proveedor, y la pantalla lo avisa. Usa su propio archivo de datos. La sesión simulada se pierde al recargar; al volver a entrar, el contador de consultas sigue donde estaba.
- **Google:** copia `.streamlit/secrets.toml.example` como `.streamlit/secrets.toml`, complétalo con el cliente OAuth de Google Cloud, define `CUENTAS_SECRETO` en `.env` e instala Authlib. Solo funciona en `localhost` o HTTPS, no por `http://IP:8501`.
- **Qué se guarda (`data/cuentas/`, fuera del repo):** un identificador seudónimo, las fechas de ingreso y los conteos de consultas por día y módulo; las consultas sin cuenta se suman sin distinguir personas. Nunca correo, nombre, tokens ni lo que la persona escribe. Los votos no se ligan a la cuenta. Se elimina tras 90 días sin uso o con «Borrar mis datos». Los totales se ven en el panel «Cómo nos va».
- **Limitación conocida:** sin cuenta, el contador vive en la sesión y se reinicia al recargar. El tope sin cuenta es un incentivo, no una barrera; la cuota de la API la protege el tope global.

## Voz: escuchar (issue #5) y dictar (issue #6)

Cada respuesta válida de los tres módulos tiene un botón **Escuchar respuesta**, con Pausar, Continuar y Detener. Usa la voz del propio navegador (`speechSynthesis`, español de Chile primero y luego otro español): Fuente Clara no llama a ninguna API de voz ni a la IA, no guarda audio y no usa `localStorage`.

- **Qué se lee:** solo la respuesta y sus citas verificadas, armadas en Python desde los mismos datos que se muestran (`modulos/voz.py`: `texto_explicame`, `texto_verifica`, `texto_estado`). No se leen menús, botones, HTML, enlaces ni otros módulos.
- **Cómo se usa en un módulo nuevo:** `voz.boton_escuchar(texto, key=None)`. La lógica de reproducción está una sola vez en `static/voz.js`; el estilo, en `static/estilo.css`.
- **Pruebas:** `python -m pytest tests/test_voz.py` (texto, botón, privacidad e integración en la app, sin red). `python scripts/probar_voz.py` abre la app en Chromium con la IA, la voz y el micrófono simulados y revisa pausar, continuar, detener, cancelar la anterior, el dictado, teclado, sin soporte y pantallas pequeñas (necesita `pip install playwright`; si ya tienes un Chrome, indica su ruta en `CHROMIUM_RUTA`). Ninguna de las dos reemplaza la prueba a mano en un celular (ver abajo).
- **Dictado (issue #6):** junto a cada campo de texto hay un botón **Dictar con el micrófono** (`voz.boton_dictar(etiqueta_del_campo)`, lógica en `static/dictado.js`). Usa el reconocimiento de voz del navegador (`SpeechRecognition`, es-CL), escribe la transcripción en el campo y la persona la revisa antes de enviar. **El audio sale del dispositivo hacia el servicio de voz del navegador** (en Chrome, Google); Fuente Clara no lo recibe ni lo guarda, y está declarado en `DECLARACION_IA.md` §5c. Dictar corta la lectura en voz alta.
- **Limitaciones conocidas:**
  - Chrome de Android no sabe pausar: al pulsar «Pausar» detenemos la lectura y lo decimos en pantalla.
  - La voz depende del dispositivo. Si no tiene ninguna en español, se avisa y no se lee (se instala en los ajustes de voz del sistema). En computadores sin voz `es-CL` se usa otra variante del español.
  - Según el sistema, la voz puede ser de red (por ejemplo, algunas de Google en Chrome). Eso lo decide el navegador, así que no prometemos que funcione sin conexión.
  - Las lecturas largas se parten en trozos de unas pocas frases para que Chrome no las corte.
  - El navegador exige un toque para empezar a hablar: nunca se lee solo.
  - **Dictado:** solo funciona en navegadores con `SpeechRecognition` (Chrome y Edge; no Firefox) y **en una conexión segura**: `localhost` o HTTPS. Abierta por `http://IP-del-computador:8501` desde el celular, el navegador bloquea el micrófono y la app lo explica; para probarlo en el celular hace falta un túnel HTTPS. Necesita conexión a internet y permiso de micrófono.

## Cambiar el documento (para la demo)

Documento cargado hoy: **Ley 21.801**, que prohíbe y regula el uso de celulares en establecimientos educacionales. Es el PDF oficial exportado desde la BCN (https://bcn.cl/122kkM, 4 páginas). El ejemplo ficticio está comentado en el catálogo; descoméntalo solo para desarrollo.

También están registradas ocho leyes más, todas en PDF oficial de la BCN: 19.628 (datos personales), 19.880 (procedimientos administrativos), 20.285 (acceso a la información pública), 20.720 (reorganización y liquidación), 21.643 (Ley Karin), 21.663 (ciberseguridad), 19.496 (consumidor) y 18.603 (partidos políticos). Las leyes 20.720 (198 páginas) y 19.496 (98 páginas) son muy largas: cada consulta manda el documento completo a la IA y puede ser lenta o superar el límite del modelo gratuito.

1. Copia el PDF o TXT oficial en `data/documentos/`. Mejor el PDF exportado de Ley Chile (BCN): trae páginas numeradas y el lector quita su encabezado repetido.
2. Regístralo **arriba** en `data/documentos/catalogo.yaml` con `titulo`, `fuente_nombre` y `fuente_url` oficial. Sin registro no aparece. Opcional: `perfiles` y `ejemplos`.
3. Revisa que se separe bien por artículo. Se reconocen "Artículo 1.-", "Artículo 2°.-", "Artículo 10 bis.-" y los numerales de leyes modificatorias ("Artículo único, numeral 4").
4. Agrega sus preguntas en `tests/preguntas_prueba.json`, bajo el nombre del archivo, y corre `scripts/evaluar.py`.

En los TXT, una línea `--- Página N ---` marca el inicio de una página nueva.

## Antes de la demo

- Verificar cada dato de `config/transparencia.yaml` en la fuente oficial y cambiar `estado: VERIFICAR` por `estado: VERIFICADO`.
- Completar `DECLARACION_IA.md` y `CHECKLIST_ETICO.md`.

## Estructura

```
app.py                     interfaz (3 pestañas, encabezado con fuente, pie fijo)
core/llm.py                capa LLM intercambiable: complete(system, user, imagen=None) -> dict
core/documento.py          carga PDF/TXT y segmenta por artículo con número de página
core/prompts.py            prompts del filtro y de los 3 módulos
core/citas.py              verificación literal de citas
core/filtro.py             filtro de alcance
core/cuentas.py            cuenta opcional: identificador seudónimo y conteos de uso (SQLite)
modulos/                   explicame.py, verifica.py, transparencia.py, comun.py, voz.py (lectura en voz alta), cuenta.py (login y topes)
config/transparencia.yaml  ley, plazos, pasos, portal y plantilla (marcados VERIFICAR)
.streamlit/config.toml     tokens de tema (colores, fuentes, radios); sin telemetría
static/                    estilo.css, voz.js, dictado.js, logo, favicon y fuentes autoalojadas
DESIGN.md                  identidad visual y reglas de diseño
design_thinking/           fichas de cada etapa de la jornada: una vacía y otra rellenada con fuentes
data/documentos/           catálogo y documento FICTICIO de ejemplo
tests/preguntas_prueba.json  casos de evaluación (requieren API)
tests/test_*.py              pruebas unitarias (sin API)
scripts/evaluar.py           evaluación con la IA
scripts/probar_app.py        prueba de integración real de los 3 módulos
scripts/probar_imagen.py     prueba real de lectura de capturas
scripts/probar_voz.py        prueba en Chromium de la lectura en voz alta (IA y voz simuladas)
scripts/smoke.py             chequeo rápido sin IA
scripts/verificar_entorno.py diagnóstico de .env, modelo y documento
```

## Principios del diseño

- Cuenta opcional y desactivada por defecto: nada de la app exige entrar (ver «Cuenta opcional»). Lo que escribe la persona vive en `st.session_state`; solo se guarda si lo autoriza al votar 👎 una respuesta.
- Las capturas de «Verifica esto» se procesan en memoria y no se guardan; solo queda el texto que la persona revisa y edita.
- Sin base vectorial: el documento completo va en el contexto del modelo.
- Una respuesta sin al menos una cita verificada no se muestra como válida.
- La app nunca envía nada: la decisión final es de la persona.
