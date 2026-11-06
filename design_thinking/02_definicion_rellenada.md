# HACKATHON </IA Aplicada>

**ETAPA 2 DE 8 | GUÍA DEL EQUIPO**

## Definición · 30 minutos

*Delimitar el problema, objetivo y alcance de la propuesta.*
**Enfoque de esta etapa:** Design Thinking: Definir | Lean Startup

[← Índice de Design Thinking](README.md) · [Ficha vacía](02_definicion_vacia.md) · [Etapa anterior: Inmersión](01_inmersion_rellenada.md)

> Completada solo con lo que está en las bases, en la Ley 21.801 (PDF oficial de la BCN, https://bcn.cl/122kkM), en la [ficha de Inmersión](01_inmersion_rellenada.md) o en este repositorio y sus issues. Cada dato lleva su fuente entre paréntesis. "Ley" es la Ley 21.801; "Bases", las bases oficiales de la hackathon; "#N", el issue N de GitHub. Lo que no sale tal cual de una fuente está marcado como **borrador** y falta acordarlo en equipo. Lo que no tenemos queda en blanco (`___`).

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

Convertir lo comprendido en un problema acotado, un objetivo claro y un alcance realista para las horas disponibles.

## Cómo usar el tiempo

| Tiempo | Actividad | Qué hacer |
|---|---|---|
| 10 min | Enunciado del problema | Redacten el problema usando: «[Actor] necesita [necesidad] porque [razón]». |
| 10 min | Objetivo medible | Definan un objetivo concreto y cómo sabrán que lo lograron (criterio de éxito). |
| 10 min | Alcance: sí / no | Decidan qué incluye el prototipo (MVP) y qué queda explícitamente fuera. Recuerden: tienen horas, no semanas. |

## Preguntas para guiarse

### ¿Podemos terminar esto en el tiempo que queda?

- **Límite:** se evalúa la versión congelada al cierre técnico de las 14:45 (Bases §3 y §12).
- **Ya funciona:** los tres módulos sobre la Ley 21.801, las citas verificadas, el guardrail contra la manipulación, el límite de uso y los votos por respuesta (`README.md`; issues cerrados #13, #24, #26 y #28).
- **Falta:** 15 issues abiertos con la etiqueta "para hoy", que significa "cabe antes del congelamiento de las 14:45". Cinco cambian la app (#1, #3, #5, #8 y #19); el resto son mediciones, documentos de ética y el pitch.
- **Si no alcanza, qué se suelta primero:** ___ (decisión de equipo).

### ¿Cómo mediremos que funciona?

- **La herramienta:** `scripts/evaluar.py` corre las 37 preguntas de prueba de la Ley 21.801: 6 normales, 5 del tema sin el dato, 3 de otro tema, 3 tendenciosas y 20 intentos de manipulación (`tests/preguntas_prueba.json`). Al final imprime la tabla de resultados por módulo (#12).
- **Verifica esto:** el mismo script compara la etiqueta que muestra la app con la esperada en 5 afirmaciones (`tests/preguntas_prueba.json`).
- **Pregúntale al Estado:** el script lista el organismo sugerido para las 5 preguntas sin el dato y una persona del equipo revisa si es razonable (#12).
- **Las personas:** votos 👍/👎 en el panel «Calidad de las respuestas» (#26) y validación con 3 a 5 personas (#18).

Metas y últimos resultados: en **Criterio de éxito**, más abajo.

### ¿Qué es lo mínimo que entrega valor?

**Borrador.** Una pregunta sobre la Ley 21.801 y su respuesta en lenguaje claro, junto a la cita literal del artículo, su página y la fuente oficial. Una respuesta sin cita verificada no se muestra como válida (`README.md`, Principios del diseño). Es lo que pide el principio rector: "que una persona entienda qué dice el documento y de dónde sale, en menos de un minuto" (`DESIGN.md` §1). Hoy es el módulo Explícame.

### ¿Qué estamos dispuestos a dejar fuera?

Lo marcado como "próximos pasos" (después del hackathon; se cuenta en el pitch) y como "decisión de equipo" (choca con lo que la app promete). La lista está en **No incluye**.

## Con foco en las personas y en lo esencial

- **Empatía:** Redacten el problema con la voz de la persona usuaria: «Necesito… porque…».

**Borrador.** No sale de conversaciones con personas: la validación del #18 sigue pendiente. Cada "necesito" es una pregunta de prueba del equipo (`tests/preguntas_prueba.json`) y cada "porque" es lo que dice la ley.

| Perfil | «Necesito… porque…» | Fuente del "porque" |
|---|---|---|
| Estudiante de media | «Necesito saber si puedo usar el celular en el recreo, porque en la media el reglamento de mi colegio puede autorizarlo en algunos espacios u horarios.» | Ley, art. 10 bis |
| Apoderado/a | «Necesito saber qué me toca hacer a mí, porque la ley me pide supervisar y acompañar el uso del celular fuera del horario escolar.» | Ley, art. único n° 2.2 |
| Docente | «Necesito saber si yo también tengo prohibido usar el celular en clases, porque la prohibición alcanza a todos los integrantes de la comunidad educativa.» | Ley, art. 10 bis |

- **Lean:** Hipótesis a demostrar: «Creemos que [solución] logrará [resultado] para [actor]. Lo sabremos si [métrica]». Está en **Hipótesis a demostrar**, al final de la ficha.

> **MIRADA ÉTICA | IA RESPONSABLE**
>
> **¿El objetivo respeta a las personas involucradas?**
>
> - En lo que ya hace el prototipo, sí: no pide login ni datos personales, lo que escribe la persona no se guarda salvo que lo autorice al votar 👎, y la persona decide, porque no hay veredictos ni envíos automáticos (`CHECKLIST_ETICO.md`; `DECLARACION_IA.md` §3 y §5b).
> - Directivos y asistentes de la educación quedan fuera del objetivo: la prohibición también los alcanza, pero la app no tiene esos perfiles (Ley, art. 10 bis; etapa 1).
> - "En menos de un minuto" puede no cumplirse para quien lee con dificultad mientras sigan pendientes la letra grande (#3), la lectura en voz alta (#5) y la revisión WCAG 2.2 AA (#19).
>
> **¿Hay algún resultado que no deberíamos buscar?**
>
> - Que la persona termine a favor o en contra de la ley. La app "no opina ni recomienda" (pie de la app).
> - Que la app diga si algo es "verdadero" o "falso", o que un pantallazo suyo sirva para "certificar" una cadena (`DECLARACION_IA.md` §3; `CHECKLIST_ETICO.md`, riesgos de mal uso).
> - Muchas solicitudes enviadas al Estado. La app no envía nada y no debe servir para inundar organismos (`CHECKLIST_ETICO.md`, riesgos de mal uso).
> - Juntar las preguntas de las personas para medir. La app promete no guardar lo que escriben (#8), y por eso cada voto guarda su contexto pero nunca el texto (`DECLARACION_IA.md` §5b).
>
> **Nuestra decisión:** **borrador.** Medimos si la persona entiende lo que dice el texto y encuentra de dónde sale. No medimos si la app la convence ni cuántas solicitudes se envían. Sobre directivos, asistentes y accesibilidad: ___

## Entregable de la etapa

Ficha de Definición: problema, objetivo, criterio de éxito y alcance (incluye / no incluye).

## Ficha de trabajo del equipo

### Enunciado del problema

**Borrador, falta acordarlo en equipo.** Con el formato «[Actor] necesita [necesidad] porque [razón]»:

> **Estudiantes, apoderados y docentes** necesitan **saber qué les prohíbe, qué les permite y qué les pide la Ley 21.801, y en qué artículo lo dice**, porque **la prohibición del celular rige desde el año escolar 2026, tiene cinco excepciones (cuatro las autoriza el director) y el texto modifica la Ley General de Educación, así que no se entiende leyéndolo solo.**

Fuentes: actores, perfiles de `catalogo.yaml`. Razón, Ley, arts. 10 bis, único y 12 transitorio (detalle en la etapa 1). Si el #18 define un único usuario concreto, el actor se reemplaza por ese usuario.

### Objetivo

**Borrador.**

> Para el congelamiento de las 14:45, que Fuente Clara responda preguntas sobre la Ley 21.801 en lenguaje claro, con la cita literal del artículo y la fuente oficial, para que una persona de la comunidad escolar entienda qué dice la ley y de dónde sale en menos de un minuto, sin que la herramienta opine.

Fuentes: Bases §3 y §12 (14:45); `README.md`; `DESIGN.md` §1; pie de la app.

### Criterio de éxito

| Qué medimos | Cómo | Meta | Último resultado |
|---|---|---|---|
| Preguntas normales con al menos una cita verificada | `evaluar.py --tipo normal` (6 casos) | 100 % (#1) | 6 de 6 |
| Intentos de manipulación rechazados | `evaluar.py --tipo manipulacion` (20 casos) | Todos (#17) | 20 de 20, todos frenados por las reglas fijas antes de llegar a la IA |
| Preguntas tendenciosas rechazadas | `evaluar.py --tipo tendenciosa` (3 casos) | Todas (#1) | 3 de 3 |
| Preguntas del tema sin el dato que ofrecen «Pregúntale al Estado» | `evaluar.py --tipo fuera` (5 casos) | ___ | 5 de 5 |
| Preguntas de otro tema detectadas, sin botón al Estado | `evaluar.py --tipo otro_tema` (3 casos) | ___ | 3 de 3 |
| Preguntas legítimas bloqueadas por error | Prueba manual con frases parecidas a un ataque ("si un alumno ignora las reglas…") | 0 (borrador) | 0 de 10* |
| Verifica esto: afirmaciones con la etiqueta esperada | `evaluar.py --modulo verifica` (5 afirmaciones) | ___ | 5 de 5 |
| Pregúntale al Estado: solicitudes con un organismo razonable | `evaluar.py --modulo estado` (5 dudas) y revisión humana (#12) | ___ | 5 de 5 |
| Tiempo promedio de respuesta | `evaluar.py`, sin contar la espera del modelo gratuito | ___ | Respuesta completa de Explícame: 10,8 s (máximo 13,7 s). Verifica esto: 9,6 s. Pregúntale al Estado: 8,0 s |
| Personas que entienden la respuesta y encuentran la cita en menos de un minuto | Validación con 3 a 5 personas (#18) | ___ | Sin validar |
| Votos positivos | Panel «Calidad de las respuestas» (#26) | ___ | Sin votos con el modelo de la demo |

Sin asterisco: medido con `python scripts/evaluar.py` el 06-11-2026 con el modelo de la demo (`claude-sonnet-5-5`, instrucciones `v-5a9f5c8`), en una sola corrida (#12). El set es chico: sirve para el pitch, pero no asegura que la app acierte con otras preguntas.

\* Medido en el #17 con la IA gratuita (`openai-fast`, instrucciones `v-6cf1d71`).

### Incluye (MVP)

Según las etiquetas de los issues ("para hoy" = cabe antes del congelamiento). Falta confirmarlo en equipo.

**Ya funciona**

- La Ley 21.801 como documento de la demo, en PDF oficial de la BCN, con los perfiles Estudiante, Apoderado/a y Docente (`catalogo.yaml`; #14).
- Los tres módulos: Explícame, Verifica esto y Pregúntale al Estado (`README.md`).
- Cada cita se busca palabra por palabra en el documento (`core/citas.py`).
- Filtro de alcance y guardrail en 3 capas contra la manipulación (#17).
- Límite de uso y mensajes de error sin datos internos (#24).
- Votos 👍/👎 con el modelo y la versión de las instrucciones, y panel de calidad (#13, #26).
- Explícame dice de qué trata el documento cuando no tiene la respuesta (#28).

**Falta para hoy**

- **Cambios en la app:** Explícame solo con lo que dice la fuente (#1), preguntas frecuentes (#8, falta verlas en el teléfono), letra grande (#3), lectura en voz alta (#5) y accesibilidad WCAG 2.2 AA (#19).
- **Medición y ética:** métricas (#12), casos de manipulación (#16, #17), usuario concreto (#18), declaración de uso de IA (#22), checklist ético (#23) y datos, sesgos y transparencia (#25).
- **Pitch:** enfoque en colegios (#14), continuidad (#20) y presentación (#21).

### No incluye

**Próximos pasos** (después del hackathon; se cuentan en el pitch):

- Filtro por tema (#2). Las otras siete leyes ya están en el catálogo, pero el caso de la demo es la Ley 21.801 (#14).
- Leer capturas de pantalla en Verifica esto (#4).
- Dictar la pregunta por micrófono (#6).
- Más fuentes oficiales para verificar (#15).
- Analítica por perfil (#27).
- Segunda revisión de cada respuesta con una IA «jueza» (#29).
- Elegir el modelo según la tarea (#30).

**Decisión de equipo** (chocan con lo que la app promete; no se hacen sin decidirlo antes):

- Análisis de contratos (#7).
- Unificador de reportes de programas de gobierno (#9).
- Contrasta tu programa (#10).
- Clave Única para opinar sobre proyectos de ley (#11).

**Fuera por las reglas del desafío o por diseño:**

- Consultas abiertas de actualidad política, candidaturas, partidos o personas en cargos públicos (Bases, Desafío 3, nota para la demostración).
- Login y base de datos (`README.md`, Principios del diseño).
- Enviar solicitudes: la persona las envía en el portal oficial (`README.md`).

**Sin decidir** (brechas de la etapa 1):

- Perfiles para directivos y asistentes de la educación: ___
- Reglamentos internos de los colegios: ___

### Hipótesis a demostrar

**Borrador.** Con el formato Lean:

> Creemos que **Fuente Clara, que responde en lenguaje claro con la cita literal del artículo y la fuente oficial y sin opinar,** logrará **que se entienda qué dice la Ley 21.801 y de dónde sale, en menos de un minuto,** para **estudiantes, apoderados y docentes**. Lo sabremos si **___ de 3 a 5 personas de la comunidad escolar entienden la respuesta y encuentran la cita en menos de un minuto (#18), y si el 100 % de las respuestas normales trae al menos una cita verificada (#1).**

## Lista de verificación

- [x] El problema nombra actor, necesidad y razón (en el borrador del enunciado)
- [ ] El objetivo es medible (hay 11 mediciones, pero 7 metas siguen en blanco)
- [ ] El alcance cabe en el tiempo disponible (quedan 15 issues "para hoy"; falta decidir qué se suelta si no alcanza)
- [ ] Todo el equipo está de acuerdo (todo lo marcado como borrador)

*Consejo: roten roles entre los 5: tiempo, registro, voz ante el mentor, apoyo técnico y control de calidad.*

---

*Hackathon IA Aplicada | Duoc UC - Pontificia Universidad Católica de Chile | Etapa 2: Definición | Equipo*
