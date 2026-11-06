# Fuente Clara

*Entender, verificar, preguntar.* Prototipo para el Desafío 3 (Democracia) de la Hackathon de IA Aplicada · Congreso Social UC 2026.

Trabaja **solo** sobre un documento público oficial precargado (un proyecto de ley) con tres módulos:

1. **Explícame:** responde en lenguaje claro, con citas verificadas del artículo exacto.
2. **Verifica esto:** pone lado a lado una cadena o post y lo que dice el texto oficial, sin veredictos.
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

## Ejecutar

```bash
streamlit run app.py
```

Para verlo en el celular, abre la "Network URL" que muestra Streamlit (mismo wifi).

## Evaluar

```bash
python scripts/evaluar.py
```

Corre `tests/preguntas_prueba.json` contra el filtro y el módulo Explícame, e imprime:

- % de respuestas con al menos una cita verificada,
- % de preguntas tendenciosas rechazadas,
- % de preguntas fuera del documento detectadas.

## Calidad de las respuestas (votos)

Bajo cada respuesta la persona vota 👍 o 👎. Los votos se guardan en `data/votos/votos.jsonl` (fuera del repo) con el modelo y la versión de las instrucciones. El enlace «Cómo nos va», al final de la app, abre el panel con los resultados. Para ver las respuestas que las personas autorizaron guardar, define `CLAVE_EQUIPO` en `.env`.

## Cambiar el documento (para la demo)

Documento cargado hoy: **Ley 21.801**, que prohíbe y regula el uso de celulares en establecimientos educacionales. Es el PDF oficial exportado desde la BCN (https://bcn.cl/122kkM, 4 páginas). El ejemplo ficticio sigue en el catálogo para desarrollo; coméntalo antes de la demo.

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
core/llm.py                capa LLM intercambiable: complete(system, user) -> dict
core/documento.py          carga PDF/TXT y segmenta por artículo con número de página
core/prompts.py            prompts del filtro y de los 3 módulos
core/citas.py              verificación literal de citas
core/filtro.py             filtro de alcance
modulos/                   explicame.py, verifica.py, transparencia.py, comun.py
config/transparencia.yaml  ley, plazos, pasos, portal y plantilla (marcados VERIFICAR)
.streamlit/config.toml     tokens de tema (colores, fuentes, radios); sin telemetría
static/                    estilo.css, logo, favicon y fuentes autoalojadas
DESIGN.md                  identidad visual y reglas de diseño
design_thinking/           fichas de cada etapa de la jornada: una vacía y otra rellenada con fuentes
data/documentos/           catálogo y documento FICTICIO de ejemplo
tests/preguntas_prueba.json
scripts/evaluar.py
```

## Principios del diseño

- Sin base de datos ni login. Lo que escribe la persona vive en `st.session_state`; solo se guarda si lo autoriza al votar 👎 una respuesta.
- Sin base vectorial: el documento completo va en el contexto del modelo.
- Una respuesta sin al menos una cita verificada no se muestra como válida.
- La app nunca envía nada: la decisión final es de la persona.
