# HACKATHON </IA Aplicada>

**ETAPA 4 DE 8 | GUÍA DEL EQUIPO**

## Desarrollo · 60 minutos

*Construcción del prototipo y sus componentes principales.*
**Enfoque de esta etapa:** Lean Startup: Construir | IA Responsable

[← Índice de Design Thinking](README.md) · [Ficha vacía](04_desarrollo_vacia.md) · [Etapa anterior: Diseño](03_diseno_rellenada.md)

> Foto del avance al **06-11-2026, 15:09**. Completada solo con lo que está en el repositorio de GitHub (`main`, las ramas del equipo, la CI y los issues), en la copia local de Becker y en las fichas anteriores. Cada dato lleva su fuente entre paréntesis; "#N" es el issue N. Lo que no sale tal cual de una fuente está marcado como **borrador** y falta acordarlo en equipo. Lo que no tenemos queda en blanco (`___`).

> **Actualización al cierre (06-11-2026):** esta ficha conserva la foto de las 15:09. Después se integraron la voz (#5), `madev` (#3 y #19), el modelo por tarea (#30) y la jueza (#29) en `main` (b21057c). La suite pasó a 293 pruebas y #29/#30 ya no son trabajo futuro; ver la fila «Segunda revisión IA y modelo por tarea» y `PITCH_CONTINUIDAD.md`.

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

Construir en paralelo los componentes principales del prototipo, priorizando lo imprescindible definido en el diseño.

## Cómo usar el tiempo

| Tiempo | Actividad | Qué hacer |
|---|---|---|
| 10 min | Preparación del entorno | Creen el repositorio compartido, configuren accesos/claves y acuerden convenciones básicas. |
| 35 min | Construcción en paralelo | Cada integrante desarrolla su componente. Primero lo imprescindible; lo deseable solo si sobra tiempo. |
| 10 min | Puntos de control | A los ~25 min y a los ~45 min, revisen el avance en voz alta (2 min cada integrante) y ajusten. |
| 5 min | Cierre de etapa | Guarden el avance (commit), anoten bloqueos y lo pendiente para la integración. |

## Preguntas para guiarse

### ¿Mi componente ya funciona solo?

- **Pruebas automáticas:** las 133 pasan en la copia local, que incluye el trabajo de voz sin commitear (`python -m pytest`, 15:09). La CI de GitHub pasó en el último commit de `main` (9f63230, 15:04).
- **Por componente:** ver **Estado por componente**, más abajo. Tres componentes funcionan solos pero todavía no están en la app: las dudas comunes, la lectura en voz alta y la accesibilidad.

### ¿Qué necesito de otro compañero?

| Quién | Necesita | De quién | Para qué | Fuente |
|---|---|---|---|---|
| Martinspyce | Que se resuelva el conflicto de su rama y se conecte en `app.py` | Becker | Unir la accesibilidad a `main` | #19: "lo que requiera tocar `app.py`, pedírselo a Becker" |
| Juan | Revisar las dos líneas que agrega la lectura en voz alta en `explicame.py` y `verifica.py`, que son sus módulos | Becker | Que no choquen con sus cambios | Copia local; #5 |
| TigreChiquito | Que alguien conecte las dudas comunes en Explícame | Juan | Que se vean en la app | #8: "Juan la conecta en Explícame" |
| Max | Los números de `scripts/evaluar.py` con el modelo de la demo | Becker | Completar `DECLARACION_IA.md` y `CHECKLIST_ETICO.md` | #12, #22, #23 |
| TigreChiquito | Métricas y costo por pregunta | Becker | Diapositivas de impacto y continuidad | #12, #20, #21 |
| TigreChiquito | Ficha de usuario concreto | Max | El pitch | #18, #21 |
| Todo el equipo | Confirmar cada dato de `config/transparencia.yaml` en la fuente oficial | — | Que la solicitud no salga "por verificar" | `README.md`, "Antes de la demo" |

### ¿Estamos construyendo lo imprescindible primero?

Sí. Las 7 funcionalidades imprescindibles de la etapa 3 ya funcionan en `main`. Lo que se construyó después son deseables (dudas comunes #8, voz #5, accesibilidad #3 y #19, métricas #12) y la lectura de capturas (#4), que estaba marcada como "próximos pasos" (historial de `main`; etapa 3).

### ¿Qué recortamos si el tiempo aprieta?

**Borrador.** Candidatos, de menos a más costoso de dejar fuera:

1. Las dudas comunes de las otras siete leyes: tienen 0 de 37 revisadas, y la demo es la Ley 21.801 (#14).
2. Mostrar la lectura de capturas en la demo (#4): ya está en `main`, pero estaba fuera del alcance de la etapa 2.
3. Unir la rama de accesibilidad (`madev`) si el conflicto no se resuelve a tiempo. La letra base de 17 px y el contraste AA ya están en `main` (`DESIGN.md` §5 y §9).

Decisión del equipo: ___

## Con foco en las personas y en lo esencial

- **Lean:** Construyan solo lo que prueba la hipótesis. Anoten cada recorte como «trabajo futuro».

La hipótesis de la etapa 2 se prueba con Explícame y sus citas verificadas, y eso ya funciona. **Trabajo futuro**, todo con la etiqueta "próximos pasos" o "decisión de equipo" en GitHub:

| Recorte | Issue |
|---|---|
| Filtro por tema entre documentos | #2 |
| Dictar la pregunta por micrófono | #6 |
| Analítica por perfil | #27 |
| Análisis de contratos · unificador de programas · contrasta tu programa · Clave Única (chocan con lo que la app promete) | #7, #9, #10, #11 |
| Dudas comunes de las otras siete leyes (0 de 37 revisadas) | #8 |
| Renovar las leyes 19.628, 20.285 y 19.496, que vencen el 30-11-2026 | #15 |

> **MIRADA ÉTICA | IA RESPONSABLE**
>
> **Si usan datos reales o sensibles, ¿están anonimizados?**
>
> - La app no usa datos reales de personas: no pide nombre ni dirección, y las preguntas de prueba y las dudas comunes las escribió el equipo (`DECLARACION_IA.md` §3; #8).
> - Si una persona autoriza guardar su pregunta al votar 👎, se ocultan RUT, correos y teléfonos antes de guardar (`core/votos.py`). Se guarda 90 días y después se elimina (`DECLARACION_IA.md` §5b; #27).
> - Las capturas de pantalla no se guardan, y la app pide no subir capturas con datos personales (`modulos/verifica.py`).
> - **Por declarar:**
>   - La rama de accesibilidad guarda las preferencias de la persona en el navegador con `localStorage` (`modulos/accesibilidad.py` en `madev`).
>   - Con la lectura en voz alta, según el dispositivo, la voz del sistema puede ser de red: eso lo decide el navegador (`modulos/voz.py`, copia local).
>
>   Ninguna de las dos está en `DECLARACION_IA.md` todavía.
>
> **¿Citamos las fuentes y verificamos lo que genera la IA?**
>
> - **Fuentes:** sí. Las 9 leyes tienen su fuente oficial, y el 06-11 se comprobó que los 9 enlaces responden y coinciden con la versión del catálogo (`FUENTES_OFICIALES.md`; #15).
> - **Citas:** sí. Cada cita se busca palabra por palabra en el documento, y una respuesta sin cita verificada no se muestra (`core/citas.py`; `README.md`).
> - **Dudas comunes de la Ley 21.801:** 10 de 10 revisadas por una persona del equipo (commit e3569a8).
> - **Falta verificar:**
>   - 10 de los 11 datos legales de la solicitud siguen marcados `VERIFICAR` (`config/transparencia.yaml`).
>   - Nadie ha revisado todavía si los organismos que sugiere la IA son razonables (#12).
>
> **Nuestra decisión:** **borrador.** No se muestra nada que la IA genere sin su cita verificada, y nada legal sin que una persona lo confirme. Antes de la demo: verificar `transparencia.yaml` y declarar `localStorage` y la voz del navegador. Responsable: ___

## Entregable de la etapa

Componentes principales funcionando de forma individual y avance guardado en un repositorio compartido.

## Ficha de trabajo del equipo

### Estado por componente (Listo / En curso / Bloqueado)

| Componente | Responsable | Estado | Evidencia |
|---|---|---|---|
| Interfaz, lógica y conexión con la IA (`app.py`, `core/`) | Becker | **Listo** | 293 pruebas pasan; CI en verde (b21057c) |
| Modelo de la demo | Becker | **Listo** | `.env` con `anthropic` / `claude-sonnet-5-5` y sin intervalo, como pedía el #30; corrida de `evaluar.py` del 06-11 anotada en `DECLARACION_IA.md` §7 |
| Segunda revisión IA y modelo por tarea | Becker | **Listo** | `core/jueza.py`, `LLM_JUEZA` / `LLM_CADENA_FILTRO` / `LLM_CADENA_JUEZA` en `core/llm.py`; `tests/test_jueza.py`; 293 pruebas en verde (b21057c) |
| Guardrail contra la manipulación | Max (casos), Becker (reglas) | **Listo** | 20 de 20 intentos rechazados (#16). Las preguntas legítimas con palabras parecidas pasan, con pruebas fijas (9f63230). El #17 sigue abierto |
| Filtro: preguntas sobre quién presentó o votó una ley, o de qué partido es alguien | Becker | **En curso** | Con el modelo gratuito no se detectaban (#17, 14:12). Se agregaron al prompt del filtro (`core/prompts.py`); falta medirlo con el modelo de la demo |
| Explícame | Juan | **Listo** | En `main`. La mejora "solo lo que dice la fuente" sigue abierta (#1) |
| Verifica esto, con captura y cámara | Juan | **Listo** | En `main` desde d969055. El #4 está marcado "próximos pasos": decidir si se muestra en la demo |
| Pregúntale al Estado | Becker | **Listo** | En `main` (`modulos/transparencia.py`) |
| Datos legales de la solicitud | Todo el equipo | **En curso** | 1 de 11 confirmados (`config/transparencia.yaml`) |
| Dudas comunes | TigreChiquito (contenido), Juan (conectar) | **En curso** | Ley 21.801: 10 de 10 revisadas (e3569a8). Ninguna pantalla llama a `faq.render`, así que no se ven en la app (`modulos/faq.py`, `app.py`) |
| Métricas | Becker | **En curso** | `evaluar.py` ya mide los tres módulos, los tiempos y los votos (e91df65). Faltan los resultados con el modelo de la demo (#12) |
| Lectura en voz alta | Martinspyce (#5) | **En curso** | `modulos/voz.py`, `static/voz.js` y el botón en los tres módulos, en la copia local de Becker, sin commitear |
| Accesibilidad: contraste, tamaño de letra y espaciado | Martinspyce (#3, #19) | **Bloqueado** | En la rama `madev`, sin unir: tiene conflicto con `main` (ver **Bloqueos**) |
| Fuentes oficiales | Max | **Listo** | `FUENTES_OFICIALES.md`, 9 fuentes verificadas el 06-11 (#15, cerrado) |
| Checklist ético | Max | **En curso** | 14 campos en blanco (`CHECKLIST_ETICO.md`; #23) |
| Declaración de uso de IA | Max | **En curso** | 8 campos en blanco; la retención de 90 días ya está (`DECLARACION_IA.md`; #22, #27) |
| Usuario concreto; datos y sesgos | Max | ___ | Sin registro: #18 y #25 sin actividad desde las 03:28 |
| Enfoque en colegios, pitch y continuidad | TigreChiquito | ___ | Sin registro en el repo (#14, #20, #21) |

### Bloqueos detectados

1. **La rama de accesibilidad (`madev`) no se puede unir sin resolver conflictos.**
   - Con `main` choca en `core/llm.py`. La rama cambia los reintentos de la IA (3 intentos con espera), un cambio que no es de accesibilidad.
   - Con el trabajo de voz de la copia local choca también en `static/estilo.css`. Se simularon ambas uniones sin tocar archivos.
   - La rama define colores en `modulos/accesibilidad.py`, pero `DESIGN.md` §3 dice que los colores viven solo en `.streamlit/config.toml` y `static/estilo.css`.
2. **Las dudas comunes revisadas no se ven en la app.** El módulo existe y tiene pruebas, pero ninguna pantalla lo llama (#8).
3. **Qué versión se evalúa.** Las bases dicen que se evalúa la versión congelada al cierre técnico de las 14:45 (Bases §3 y §12). Según la hora de cada corrida de la CI, lo último que se subió a `main` antes de las 14:45 fue e91df65 (14:38). Después se subieron 8b8208d (14:56) y e3569a8, dc3507e y 9f63230 (15:04). Confirmar con la organización: ___
4. **El modelo gratuito no sirve para la demo.** Tardaba entre 45 y 75 s por llamada y se quedaba sin tokens (#17, #30). El `.env` ya apunta a Anthropic, pero falta probarlo.
5. **Los datos legales de la solicitud aparecen como "por verificar" en pantalla** mientras no se confirmen (`config/transparencia.yaml`).

### Pendiente para la integración

En orden sugerido (**borrador**):

1. **Guardar la lectura en voz alta (#5):** commit de `modulos/voz.py`, `static/voz.js` y los cambios en los tres módulos y en `estilo.css`, después de correr `python -m pytest`.
2. **Unir `madev`:**
   - Resolver `core/llm.py` y `static/estilo.css`.
   - Decidir si se quedan los reintentos nuevos.
   - Mover los colores a los archivos de tema (`DESIGN.md` §3).
   - Conectar el interruptor en `app.py` (#19).
3. **Conectar las dudas comunes en Explícame** (#8, Juan).
4. **Correr `python scripts/evaluar.py` con el modelo de la demo** y anotar los resultados en el #12, `DECLARACION_IA.md` y `CHECKLIST_ETICO.md`. Incluye las preguntas sobre quién presentó o votó una ley (#17).
5. **Confirmar los 10 datos de `config/transparencia.yaml`** que faltan y cambiarlos a `VERIFICADO`.
6. **Declarar** `localStorage` (accesibilidad) y la voz del navegador en `DECLARACION_IA.md`.
7. **Decidir si la lectura de capturas (#4) se muestra en la demo.**

Ya resuelto: el ejemplo ficticio está comentado en el catálogo, como pedía el `README.md` antes de la demo (`data/documentos/catalogo.yaml`).

## Lista de verificación

- [x] Repositorio compartido activo (GitHub, con ramas por persona y CI que corre las pruebas en cada envío)
- [x] Cada componente tiene un responsable (etiqueta por área en los issues)
- [ ] Hicimos los 2 puntos de control (sin registro)
- [x] Avance guardado antes de cerrar (voz y accesibilidad integradas; 293 pruebas en verde)

*Consejo: roten roles entre los 5: tiempo, registro, voz ante el mentor, apoyo técnico y control de calidad.*

---

*Hackathon IA Aplicada | Duoc UC - Pontificia Universidad Católica de Chile | Etapa 4: Desarrollo | Equipo*
