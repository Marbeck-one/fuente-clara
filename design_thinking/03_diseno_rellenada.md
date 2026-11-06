# HACKATHON </IA Aplicada>

**ETAPA 3 DE 8 | GUÍA DEL EQUIPO**

## Diseño · 30 minutos

*Funcionalidades, arquitectura, tecnologías y experiencia de usuario.*
**Enfoque de esta etapa:** Design Sprint: Esbozar y decidir | IA Responsable

[← Índice de Design Thinking](README.md) · [Ficha vacía](03_diseno_vacia.md) · [Etapa anterior: Definición](02_definicion_rellenada.md)

> Completada solo con lo que está en las bases, en las fichas anteriores o en este repositorio: el código de `main`, las ramas del equipo y los issues. Cada dato lleva su fuente entre paréntesis. "Bases" son las bases oficiales de la hackathon; "#N", el issue N de GitHub. Lo que está en una rama y todavía no en `main` lo dice. Lo que no sale tal cual de una fuente está marcado como **borrador** y falta acordarlo en equipo. Lo que no tenemos queda en blanco (`___`).

## Datos del equipo

| | |
|---|---|
| **Nombre del equipo** | ___ (el proyecto se llama Fuente Clara: `README.md`) |
| **Mesa N°** | ___ |
| **Mentor/a del equipo** | ___ |
| **Integrante 1** | Becker (Marbeck-one) |
| **Integrante 2** | Juan (SrJuanPi) |
| **Integrante 3** | Max (Psychosaur) |
| **Integrante 4** | TigreChiquito |
| **Integrante 5** | Martinspyce |

Integrantes tal como aparecen como responsables en los issues de GitHub.

## Objetivo de la etapa

Planificar cómo se construirá la solución: qué hará, con qué tecnologías, cómo se conectan sus partes y cómo la usará la persona.

## Cómo usar el tiempo

| Tiempo | Actividad | Qué hacer |
|---|---|---|
| 8 min | Funcionalidades | Listen las funcionalidades del MVP y ordénenlas por prioridad (imprescindible / deseable). |
| 8 min | Arquitectura y tecnologías | Dibujen un diagrama simple de componentes (datos, lógica, modelo de IA, interfaz) y elijan herramientas que dominen. |
| 7 min | Experiencia de usuario | Bosquejen en papel o pizarra el flujo principal de la persona usuaria (2–4 pantallas o pasos). |
| 7 min | Reparto de trabajo | Asignen responsables por componente y definan cómo se integrará el trabajo. |

## Preguntas para guiarse

### ¿Dónde interviene la IA y por qué ahí?

La IA interviene solo donde hay que leer o escribir lenguaje natural. Todo lo que se puede comprobar con reglas lo hace el código (`DECLARACION_IA.md` §2–§4).

| Paso | ¿IA? | Por qué | Dónde |
|---|---|---|---|
| Límite de uso | No | Contar consultas no necesita IA | `core/limites.py` |
| Rechazar intentos típicos de manipulación ("ignora tus instrucciones") | No | Se detectan con reglas fijas, sin gastar una llamada | `core/guardrail.py`, capa 1 |
| Filtro de alcance: dentro del documento, sin el dato, otro tema u opinión | **Sí** | Hay que entender una pregunta escrita con las palabras de cada persona | `core/filtro.py` |
| Explícame: pasar el texto legal a lenguaje claro | **Sí** | Es traducción de lenguaje | `modulos/explicame.py` |
| Verifica esto: separar la cadena en afirmaciones y ubicar el texto oficial | **Sí** | Es lectura de lenguaje | `modulos/verifica.py` |
| Pregúntale al Estado: sugerir el organismo y redactar la solicitud | **Sí** | Es redacción; el organismo se muestra como "sugerencia de la IA" | `modulos/transparencia.py` |
| Leer el texto de una captura de pantalla | **Sí** | Es lectura de imagen | Rama `srjuanpi` (#4), aún no está en `main` |
| Comprobar que cada cita está tal cual en el documento | No | Tiene que ser exacto y no depender del modelo | `core/citas.py` |
| Bloquear respuestas que opinan, dan veredicto o traen enlaces | No | Es el control sobre lo que escribió la IA | `core/guardrail.py`, capa 3 |
| Etiquetas del verificador ("El texto lo respalda"…) | No | Las fija la app para que la IA no dé veredictos | `modulos/verifica.py` |
| Ley, portal, pasos y plazos de la solicitud | No | Son datos jurídicos: los revisa el equipo | `config/transparencia.yaml` |
| Dudas comunes | No | Respuestas preparadas y revisadas por el equipo | Rama `TigreChiquito` (#8), aún no está en `main` |

Una pregunta en Explícame llama dos veces a la IA: una para el filtro y otra para la respuesta. Si el filtro la rechaza, la segunda llamada no se hace (`modulos/explicame.py`).

### ¿Qué datos necesitamos y los tenemos?

| Dato | ¿Lo tenemos? | Fuente |
|---|---|---|
| Documento oficial de la demo | Sí: Ley 21.801, PDF de la BCN | `data/documentos/catalogo.yaml` |
| Otros documentos | Sí: ocho leyes más en PDF de la BCN, más un ejemplo ficticio para desarrollo | `catalogo.yaml` |
| Ley, portal, pasos, plazos y plantilla de la solicitud | Sí, pero todos dicen `estado: VERIFICAR`, y en la app aparecen como "por verificar" | `config/transparencia.yaml`; `README.md`, "Antes de la demo" |
| Preguntas de prueba | Sí: 27 preguntas y 5 afirmaciones para la Ley 21.801 | `tests/preguntas_prueba.json` |
| Dudas comunes revisadas | No todavía: hay 8 para la Ley 21.801, todas con `revisada: false`, así que ninguna se muestra | Rama `TigreChiquito` (#8) |
| Usuario concreto y su validación | No | #18 |
| Datos de personas | No los necesitamos: la app no pide nombre, dirección ni otros datos | `DECLARACION_IA.md` §3 |
| Clave de IA para la demo | ___ (el equipo recibirá una de Anthropic) | #30 |

### ¿Qué herramienta dominamos de verdad?

Toda la app está en Python, Streamlit y archivos YAML, y los aportes del equipo en el repo y en las ramas están en esas mismas herramientas (`requirements.txt`; historial de git). Qué domina cada integrante: ___

### ¿Cómo se juntarán las piezas al final?

- **Hoy:** no hay pull requests. Juan y TigreChiquito trabajan en sus ramas (`srjuanpi` y `TigreChiquito`), y Becker une el trabajo en `main` y lo conecta en `app.py`. La etiqueta "núcleo" incluye la integración, y los issues #2 y #3 dicen "Becker la conecta en `app.py`". Los PDF de Max se registraron así (commits 05371b9 y d46ecd7).
- **Conflictos previstos:** se simuló la unión de las ramas sin tocar archivos (06-11-2026):
  - `main` + `TigreChiquito`: conflicto en `data/documentos/catalogo.yaml`. Las dos registraron las leyes nuevas.
  - `main` + `srjuanpi`: conflicto en `catalogo.yaml`.
  - Al unir las dos ramas, también hay conflicto en `app.py`.
  - En la copia local de `main` hay además cambios sin commitear en `core/llm.py`, `modulos/verifica.py` y `scripts/evaluar.py`, archivos que la rama `srjuanpi` también modifica.
- **Pruebas al unir:** la rama `srjuanpi` agrega pruebas automáticas (pytest) y CI en GitHub Actions, que compila y corre las pruebas en cada envío (`.github/workflows/ci.yml` en esa rama).
- **Orden de unión y hora límite antes de las 14:45:** ___ (decisión de equipo).

## Con foco en las personas y en lo esencial

- **Empatía:** Bosquejen el flujo desde la perspectiva del usuario, considerando personas con otras capacidades o contextos.

| Persona o contexto | Qué ya considera el diseño | Qué falta |
|---|---|---|
| Baja visión o personas mayores | Letra base de 17 px y fuente Atkinson Hyperlegible, hecha para baja visión; contraste AA en todos los textos (`DESIGN.md` §5 y §9) | Letra grande (#3); revisión WCAG 2.2 AA (#19) |
| Prefiere escuchar o hablar | — | Leer en voz alta (#5, para hoy); dictado (#6, próximos pasos) |
| Usa lector de pantalla o teclado | Foco visible y botones de 44 px o más (`DESIGN.md` §9) | Prueba con teclado y TalkBack (#19) |
| Le cuesta distinguir colores | Nada se comunica solo con color (`DESIGN.md` §4) | — |
| Sensible al movimiento | Con "reducir movimiento" activado, las animaciones se apagan (`DESIGN.md` §8) | — |
| Baja alfabetización digital o lectora | Lenguaje de 8° básico (`DECLARACION_IA.md` §2); ejemplo de pregunta en cada campo | Validar con personas (#18) |
| Usa el celular | Funciona en el teléfono con la "Network URL" (`README.md`) | Preguntas frecuentes en el teléfono (#8) |
| La duda está en una captura | — | Leer capturas: en la rama `srjuanpi` (#4) |
| No tiene cuenta ni quiere registrarse | Sin login (`README.md`, Principios) | — |
| Mala conexión en el evento | — | Plan B con capturas o video (#21) |

- **Lean:** Elijan la funcionalidad que prueba la hipótesis y dejen fuera el resto.

**Borrador.** La hipótesis de la etapa 2 se prueba con **Explícame**: respuesta en lenguaje claro con la cita literal del artículo y la fuente oficial. Lo demás se ordena en **Funcionalidades**, más abajo.

> **MIRADA ÉTICA | IA RESPONSABLE**
>
> **¿Qué datos necesitamos y con qué permiso los usamos?**
>
> | Dato | Permiso o resguardo | Fuente |
> |---|---|---|
> | Documentos oficiales | Son públicos; cada uno con su fuente oficial en pantalla | `catalogo.yaml` |
> | Lo que escribe la persona | Se envía al proveedor de IA para responder y no se guarda. La app avisa que no se escriban datos personales. Retención del proveedor: ___ | `DECLARACION_IA.md` §5 |
> | Pregunta y respuesta de un voto 👎 | Solo si la persona marca la casilla. Se ocultan RUT, correos y teléfonos, y solo el equipo lo lee, con clave. Retención: ___ | `DECLARACION_IA.md` §5b |
> | Votos 👍/👎 | Guardan su contexto (pestaña, modelo, versión), nunca el texto | `DECLARACION_IA.md` §5b |
> | Capturas de pantalla | Se envían al modelo para leerlas y no se guardan. La app avisa que no se suban capturas con datos personales | Rama `srjuanpi` (#4) |
> | Ley de datos personales aplicable | ___ (falta confirmarla en la BCN) | #25 |
>
> **¿Dónde debe haber supervisión humana?** Las bases piden un punto de decisión humana explícito (Bases §10).
>
> - **Antes de la demo, el equipo:** compara cada PDF con su fuente oficial (`CHECKLIST_ETICO.md`), confirma cada dato de `transparencia.yaml` (`README.md`), lee cada duda común contra la ley antes de marcarla `revisada: true` (rama `TigreChiquito`) y revisa si el organismo sugerido es razonable (#12).
> - **Durante el uso, la persona:** decide en Verifica esto, porque la app no da veredictos (`DESIGN.md` §1). Marca "Revisé el borrador y entiendo que yo decido si enviarlo" antes de ver el enlace al portal (`modulos/transparencia.py`). Revisa y corrige el texto leído de una captura antes de compararlo (rama `srjuanpi`).
> - **Después, el equipo:** lee las respuestas 👎 autorizadas para corregir las instrucciones de la IA (`DECLARACION_IA.md` §5b) y valida el checklist ético en los dos checkpoints (`CHECKLIST_ETICO.md`).
>
> **Nuestra decisión:** **borrador.** La IA lee y redacta. Las citas las comprueba el código y los datos legales los confirma una persona del equipo. Lo que pasa fuera de la app (enviar una solicitud, compartir una comparación) lo hace la persona. Pendiente: retención del proveedor y ley de datos aplicable: ___

## Entregable de la etapa

Ficha de Diseño: lista priorizada de funcionalidades, diagrama de arquitectura, tecnologías y reparto de responsabilidades.

## Ficha de trabajo del equipo

### Funcionalidades (imprescindibles / deseables)

**Borrador de prioridades, falta acordarlo en equipo.** El estado sale del código y de los issues.

**Imprescindibles**

| # | Funcionalidad | Estado | Por qué es imprescindible |
|---|---|---|---|
| 1 | Explícame con cita verificada (artículo, página y fuente oficial) | Funciona. Mejora pendiente: #1 | Prueba la hipótesis (etapa 2) |
| 2 | Documento y fuente oficial siempre visibles arriba, con el modelo de IA activo | Funciona (`app.py`) | Trazabilidad de fuentes (Bases, Desafío 3) |
| 3 | Filtro de alcance con mensaje fijo "Fuente Clara no opina" | Funciona (`core/filtro.py`) | Neutralidad política verificable (Bases, Desafío 3) |
| 4 | Guardrail en 3 capas contra la manipulación | Funciona. Faltan los casos de Max: #16, #17 | Mecanismos contra la manipulación (Bases, Desafío 3) |
| 5 | Pregúntale al Estado con casilla de confirmación antes del portal | Funciona. Datos legales por verificar (`transparencia.yaml`) | Punto de decisión humana (Bases §10) |
| 6 | Verifica esto sin veredictos | Funciona (`modulos/verifica.py`) | Está en el guion de la demo (#21) |
| 7 | Límite de uso | Funciona (#24) | Protege la cuota de la API en el evento (`CHECKLIST_ETICO.md`) |

**Deseables**

| Funcionalidad | Estado | Etiqueta |
|---|---|---|
| Explícame solo con lo que dice la fuente, frase por frase | Abierto (#1) | Para hoy |
| Dudas comunes con cita, sin IA | En la rama `TigreChiquito`; 0 de 8 revisadas (#8) | Para hoy |
| Letra grande (#3) y lectura en voz alta (#5) | Abiertos | Para hoy |
| Accesibilidad WCAG 2.2 AA | Abierto (#19) | Para hoy |
| Votos 👍/👎 y panel «Calidad de las respuestas» | Funciona (#26) | Para hoy (cerrado) |
| Elegir entre las nueve leyes del catálogo | Funciona (`app.py`); la demo es la Ley 21.801 (#14) | — |
| Leer capturas de pantalla en Verifica esto | En la rama `srjuanpi` (#4) | Próximos pasos: **decidir si entra hoy**, porque la etapa 2 la dejó fuera |

### Diagrama de arquitectura (dibujar)

Sacado del código de `main`. Cada consulta recorre los pasos en este orden (`modulos/comun.py`, `core/filtro.py`, `modulos/explicame.py`).

```text
 PERSONA  (celular o computador, sin login)
    │  escribe una pregunta, una cadena o una duda
    ▼
┌─ INTERFAZ ─ app.py + modulos/  (Streamlit) ───────────────────────────────┐
│  Documento y fuente oficial arriba · 3 pestañas:                          │
│  Explícame · Verifica esto · Pregúntale al Estado · panel de calidad      │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   ▼
┌─ LÓGICA ─ core/ ──────────────────────────────────────────────────────────┐
│  1. limites.py     ¿cabe en el límite de uso?                 sin IA      │
│  2. guardrail.py   ¿es un intento típico de manipulación?     sin IA      │
│  3. filtro.py      ¿dentro, sin el dato, otro tema u opinión? ──┐         │
│  4. prompts.py     instrucción + documento completo + texto   ──┤         │
│  5. llm.py         llama al modelo ◄────────────────────────────┘         │
│  6. citas.py       ¿cada cita está tal cual en el documento?  sin IA      │
│  7. guardrail.py   ¿opinó, dio veredicto o puso enlaces?      sin IA      │
└───────────┬───────────────────────────────────────┬───────────────────────┘
            │                                       │
            ▼                                       ▼
┌─ MODELO DE IA ─────────────────┐   ┌─ DATOS ─────────────────────────────────┐
│ Anthropic, OpenAI o Google,    │   │ data/documentos/ PDF de la BCN          │
│ según LLM_PROVIDER en .env.    │   │   + catalogo.yaml → documento.py        │
│ Recibe el documento completo   │   │   (separa por artículo y página)        │
│ y el texto de la persona.      │   │ config/transparencia.yaml (ley, plazos) │
│ llm.py no registra lo enviado. │   │ data/votos/votos.jsonl (fuera del repo, │
└────────────────────────────────┘   │   solo si la persona vota)              │
                                     └─────────────────────────────────────────┘
```

Sin base de datos, sin login y sin base vectorial: el documento completo va en cada consulta (`README.md`, Principios del diseño).

### Tecnologías elegidas

| Capa | Tecnología | Para qué | Fuente |
|---|---|---|---|
| Lenguaje | Python 3.11 o superior | Todo el proyecto | `README.md` |
| Interfaz | Streamlit 1.66.1 | Pantallas, pestañas, formularios; se abre en el celular | `requirements.txt` |
| Documentos | pypdf 6.21.4 | Leer los PDF oficiales | `requirements.txt` |
| Configuración y datos | PyYAML, python-dotenv | Catálogo, datos de transparencia y claves en `.env` | `requirements.txt` |
| Modelo de IA | SDK de Anthropic, OpenAI y Google, intercambiables | Demo: Anthropic (`claude-sonnet-5-5` por defecto). Pruebas: Pollinations `openai-fast`, gratis y no apto para la demo | `core/llm.py`; `.env.example`; #30 |
| Panel de calidad | pandas, Altair | Gráficos de los votos | `requirements.txt` |
| Diseño | Atkinson Hyperlegible Next y Source Serif 4, autoalojadas | Lectura fácil y citas en serif; ninguna petición a terceros | `DESIGN.md` §5 |
| Pruebas | `scripts/evaluar.py`; pytest y CI en GitHub Actions en la rama `srjuanpi` | Métricas para el pitch y pruebas en cada envío | `README.md`; rama `srjuanpi` |
| Trabajo en equipo | GitHub: issues con etiquetas por área y ramas por persona | Reparto e integración | Issues; `git branch -a` |

### Bosquejo del flujo de usuario

Flujo principal en 4 pasos (`app.py`, `modulos/explicame.py`, `modulos/transparencia.py`):

1. **Abrir.** Ve qué documento está leyendo y su fuente oficial ("Estás leyendo"). Si hay más de uno, lo elige.
2. **Preguntar.** En Explícame escribe su duda con sus palabras. Si quiere, elige su perfil: Estudiante, Apoderado/a o Docente.
3. **Leer.** Ve la respuesta, "Qué cambia para ti" y "De dónde sale": cada cita con su artículo, su página y el texto oficial resaltado.
4. **Decidir.** Vota 👍/👎 si quiere. Si el documento no responde, pasa a Pregúntale al Estado con la duda ya escrita.

```text
[1 Abrir] ──► [2 Preguntar] ──► filtro ──► [3 Leer respuesta + citas] ──► [4 Decidir: 👍/👎]
                                  │
                                  ├─ pide opinión ───► "Fuente Clara no opina" (mensaje fijo)
                                  ├─ otro tema ──────► aviso de qué trata el documento
                                  └─ sin el dato ────► botón "Pregúntale al Estado"
                                                       │
                                                       ▼
                                                       borrador de solicitud
                                                       │
                                                       ▼
                                                       ☑ "Revisé el borrador…"
                                                       │
                                                       ▼
                                                       enlace al Portal de Transparencia
                                                       (la persona envía, no la app)
```

Si la respuesta no trae ninguna cita verificada, no se muestra: aparece "No pudimos comprobar esta respuesta" (`modulos/explicame.py`).

### Responsables por componente

Según las etiquetas de los issues, que tienen una por área y persona:

| Componente | Archivos | Responsable |
|---|---|---|
| Núcleo e integración: interfaz, lógica, IA, Pregúntale al Estado | `app.py`, `core/`, `modulos/transparencia.py`, `modulos/comun.py` | Becker (Marbeck-one) |
| Respuestas neutrales de Explícame y Verifica esto; leer capturas | `modulos/explicame.py`, `modulos/verifica.py`, prompts de esos módulos | Juan (SrJuanPi) |
| Accesibilidad, voz y lectura fácil | `static/estilo.css`, `.streamlit/config.toml`, módulo nuevo de voz o accesibilidad | Martinspyce |
| Contenido: documentos, dudas comunes y pitch | `data/documentos/catalogo.yaml`, `data/faq/`, `modulos/faq.py`, `tests/preguntas_prueba.json` | TigreChiquito |
| Datos y ética: métricas, checklist, declaración de IA, usuario y PDF oficiales | `CHECKLIST_ETICO.md`, `DECLARACION_IA.md`, casos de manipulación, ficha de usuario | Max (Psychosaur) |

Reglas de integración que ya están en los issues: lo que toque `app.py` se le pide a Becker (#19). Si alguien cambia las reglas comunes de la IA (`REGLAS_BASE`), avisa a Becker (#1). Para conectar cada pieza: las dudas comunes las conecta Juan en Explícame (#8); la letra grande y el filtro por tema, Becker en `app.py` (#3, #2); el botón "Escuchar" lo agrega cada dueño en su módulo (#5).

## Lista de verificación

- [ ] Funcionalidades priorizadas (hay una propuesta; falta acordarla)
- [x] Diagrama de componentes dibujado (en esta ficha, sacado del código)
- [ ] Tecnologías acordadas y accesibles (ya están en uso en la app; falta confirmar la clave de Anthropic para la demo, #30)
- [x] Cada integrante sabe qué construirá (cada uno tiene issues asignados y una etiqueta con su área)

*Consejo: roten roles entre los 5: tiempo, registro, voz ante el mentor, apoyo técnico y control de calidad.*

---

*Hackathon IA Aplicada | Duoc UC - Pontificia Universidad Católica de Chile | Etapa 3: Diseño | Equipo*
