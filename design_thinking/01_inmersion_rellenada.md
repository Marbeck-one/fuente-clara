# HACKATHON </IA Aplicada>

**ETAPA 1 DE 8 | GUÍA DEL EQUIPO**

## Inmersión · 45 minutos

*Análisis del desafío: necesidades, actores, restricciones.*
**Enfoque de esta etapa:** Design Thinking: Empatizar | IA Responsable

[← Índice de Design Thinking](README.md) · [Ficha vacía](01_inmersion_vacia.md)

> Completada solo con lo que está en las bases, en la Ley 21.801 (PDF oficial de la BCN, https://bcn.cl/122kkM) o en este repositorio. Cada dato lleva su fuente entre paréntesis. "Ley" es la Ley 21.801; "Bases", las bases oficiales de la hackathon. Lo que no tenemos queda en blanco (`___`).

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

Comprender a fondo el desafío antes de proponer soluciones: qué problema existe, a quién afecta y bajo qué límites debe resolverse.

## Cómo usar el tiempo

| Tiempo | Actividad | Qué hacer |
|---|---|---|
| 10 min | Lectura del desafío | Lean el enunciado completo de forma individual y luego subrayen en conjunto las palabras clave. |
| 15 min | Mapa de actores | Identifiquen quiénes están involucrados (usuarios, beneficiarios, quienes deciden, quienes operan) y qué necesita cada uno. |
| 10 min | Necesidades y restricciones | Listen necesidades concretas y restricciones: tiempo, datos disponibles, tecnología, normativa, presupuesto. |
| 10 min | Síntesis y consenso | Prioricen las 3 necesidades más relevantes y acuerden una frase que resuma el desafío con sus propias palabras. |

## Preguntas para guiarse

### ¿Quién sufre realmente este problema y cuándo?

- En el desafío: "muchas personas, en especial jóvenes, no entienden cómo funcionan los procesos legislativos, presupuestarios o electorales, ni cómo participar más allá del voto" (Bases, Desafío 3).
- En nuestro caso: estudiantes, apoderados y docentes de los establecimientos que imparten educación parvularia, básica o media (Ley, art. 10 bis; perfiles en `data/documentos/catalogo.yaml`).
- Desde cuándo: la prohibición rige desde el inicio del año escolar 2026, y los colegios tenían hasta el 30 de junio de 2026 para actualizar su reglamento interno (Ley, art. 12 transitorio).

### ¿Qué sabemos y qué estamos suponiendo?

**Sabemos** (hechos con fuente):

- La prohibición "se extenderá a todos los integrantes de la comunidad educativa, salvo en los casos excepcionales que contempla este artículo" (Ley, art. 10 bis).
- Hay cinco excepciones (letras a–e). Cuatro de ellas (a, c, d en actividades curriculares, y e) necesitan autorización expresa del director (Ley, art. 10 bis).
- En media, los reglamentos de cada colegio pueden disponer "espacios, horarios o actividades específicas" en que el celular esté autorizado (Ley, art. 10 bis).
- Los apoderados deben "supervisar y acompañar el uso" del celular fuera del horario escolar (Ley, art. único n° 2.2).
- La ley no se lee sola: modifica la Ley N° 20.370, General de Educación ("Introdúcense las siguientes modificaciones en el decreto con fuerza de ley N° 2, de 2009…") (Ley, art. único).
- El prototipo ya tiene tres módulos: Explícame, Verifica esto y Pregúntale al Estado (`README.md`).

**Suponemos o no sabemos todavía** (no está validado con personas):

- Dónde se informan hoy, qué barreras tienen y en qué dispositivo usarían la app (#18, pendiente).
- Si los perfiles, los ejemplos y las preguntas de prueba suenan como hablan estudiantes y apoderados (#14, pendiente).
- Si la letra de 17 px y las pestañas con ícono se leen bien (`DESIGN.md`, Pendientes 2).
- Si la paleta de colores se asocia a alguna coalición política (`DESIGN.md`, Pendientes 1).
- Cuánto rechaza el filtro las preguntas tendenciosas y los intentos de manipulación: los resultados siguen en blanco (`CHECKLIST_ETICO.md`; #12).

### ¿Qué pasaría si no se resolviera?

- Según las bases: "La circulación de desinformación en redes sociales y mensajería, los contenidos generados por IA (deepfakes, textos sintéticos) y la desconfianza en las instituciones afectan la calidad del debate público" (Bases, Desafío 3).
- En el caso de la Ley 21.801: ___ (no tenemos datos).

### ¿Qué restricciones no son negociables?

- Neutralidad política verificable, trazabilidad de fuentes, no generar contenido persuasivo partidista y mecanismos para evitar que la herramienta se use para manipular (Bases, Desafío 3, restricciones éticas).
- La demo se hace solo sobre documentos precargados y verificados, con la fuente oficial en pantalla. Nada de consultas abiertas de actualidad política, candidaturas, partidos ni personas en cargos públicos (Bases, Desafío 3, nota para la demostración).
- El checklist ético, completo y validado en los dos checkpoints antes de las 14:45, es requisito de admisibilidad (Bases §12).
- Toda solución mantiene un punto de decisión humana explícito (Bases §10).
- No se usan datos sensibles reales de personas sin resguardo y consentimiento explícito (Bases, Condiciones generales).

## Con foco en las personas y en lo esencial

- **Empatía:** Conversen con 1 o 2 personas afectadas (usuarios, compañeros, comunidad) y anoten qué dijeron, no solo lo que suponen.

No hay registro en el repo de conversaciones con personas afectadas. El #18 pide validar con 3 a 5 personas durante la jornada.

| Persona (rol, sin nombre) | Qué dijo (textual) |
|---|---|
| ___ | ___ |
| ___ | ___ |

> **MIRADA ÉTICA | IA RESPONSABLE**
>
> **¿A quién podría afectar negativamente esta solución?**
>
> - A quien recibe una cadena "certificada" con un pantallazo de Verifica esto (`CHECKLIST_ETICO.md`, riesgos de mal uso).
> - A los organismos públicos, si se usa Pregúntale al Estado para inundarlos de solicitudes (`CHECKLIST_ETICO.md`, riesgos de mal uso).
> - A quien confía en una explicación equivocada: la verificación comprueba que el texto citado existe en el documento, no que la explicación sea correcta (`DECLARACION_IA.md` §7).
> - A quien escribe distinto (informal o con faltas de ortografía), si el filtro lo rechaza por error. El filtro puede equivocarse con preguntas ambiguas (`CHECKLIST_ETICO.md`, Sesgos; `DECLARACION_IA.md` §7).
>
> **¿Quién queda fuera o no está representado?**
>
> - Quien no puede leer bien la pantalla o prefiere la voz: letra grande (#3), lectura en voz alta (#5), dictado (#6) y WCAG 2.2 AA (#19) siguen pendientes.
> - Quien tiene la duda en una captura de pantalla: leer capturas está pendiente (#4).
> - Directivos y asistentes de la educación: la prohibición también los alcanza (Ley, art. 10 bis), pero la app solo tiene los perfiles Estudiante, Apoderado/a y Docente (`catalogo.yaml`).
> - Quien necesita lo que dice el reglamento de su colegio: hoy la app solo tiene la ley (más documentos: #2 y #14).
>
> **Nuestra decisión:** lo que ya está decidido en el prototipo. La IA no opina ni da veredictos. Cada respuesta muestra su cita y la fuente oficial. No hay login ni base de datos. La app no envía nada: la persona revisa y decide (`README.md`, Principios del diseño; `CHECKLIST_ETICO.md`). Sobre las brechas de la lista anterior: ___

## Entregable de la etapa

Ficha de Inmersión completada: actores, necesidades priorizadas (top 3) y restricciones.

## Ficha de trabajo del equipo

### Desafío en una frase (con sus palabras)

**Borrador, falta acordarlo en equipo.** Está armado con frases que ya están en el repo:

> Que estudiantes, apoderados y docentes entiendan qué dice la Ley 21.801 y de dónde sale, en menos de un minuto, sin que la herramienta opine ni recomiende.

Fuentes: perfiles de `catalogo.yaml`, principio rector de `DESIGN.md` §1 ("que una persona entienda qué dice el documento y de dónde sale, en menos de un minuto") y pie de la app ("No opina ni recomienda").

### Actores clave y qué necesita cada uno

| Actor | Tipo | Qué le dice la ley | Qué necesita saber (preguntas de prueba del equipo) |
|---|---|---|---|
| Estudiantes | Usuario y beneficiario | El celular está prohibido, salvo las excepciones; en media, el reglamento puede autorizar espacios u horarios (Ley, art. 10 bis) | "¿Puedo usar el celular en el recreo si estoy en la media?", "¿En qué casos se permite usar el celular en el colegio?", "¿Qué pasa si un estudiante ignora las reglas del colegio sobre el celular?" |
| Apoderados | Usuario y beneficiario | Supervisar y acompañar el uso fuera del horario escolar, y asumir la responsabilidad por su uso indebido (Ley, art. único n° 2.2). Acreditan con certificado las excepciones a y c, y pueden pedir la e (Ley, art. 10 bis) | "¿Qué les toca hacer a los apoderados según esta ley?" |
| Docentes | Usuario y beneficiario | La prohibición también los alcanza, especialmente en la sala de clases; se permite si es útil para la enseñanza, letra d (Ley, art. 10 bis) | "¿Los profesores también tienen prohibido usar el celular en clases?" |
| Director/a | Decide | Autoriza expresamente las excepciones a, c, d (curriculares) y e (Ley, art. 10 bis) | ___ |
| Establecimientos educacionales | Deciden | Disponen medidas para aplicar la prohibición y las excepciones, actualizan su reglamento interno (hasta el 30-jun-2026) e informan a la comunidad sobre el uso responsable (Ley, arts. 10 bis y 12 transitorio) | ___ |
| Superintendencia de Educación | Decide | Dicta las instrucciones para actualizar los reglamentos internos (Ley, art. 10 bis y 12 transitorio) | ___ |
| Mineduc, con Segegob y Desarrollo Social | Opera | Campaña anual de difusión (Ley, art. 10 quater); evaluación de la ley en marzo de 2030 (Ley, art. 12 transitorio) | ___ |
| Portal de Transparencia | Opera | — | Donde la persona envía la solicitud que prepara Pregúntale al Estado (`README.md`) |
| Equipo Fuente Clara | Opera | — | Mantiene el catálogo de documentos y los compara con la fuente oficial antes de la demo (`CHECKLIST_ETICO.md`) |

Usuarios que nombran las bases para el Desafío 3: votantes jóvenes, organizaciones de la sociedad civil, municipios, medios locales y establecimientos educacionales (formación ciudadana). El equipo se enfoca en los establecimientos educacionales (#14).

### Top 3 necesidades

**Propuesta, falta acordarla en equipo.** Una por módulo del prototipo, cada una ligada a lo que piden las bases:

1. **Entender qué dice la ley en lenguaje claro, con la fuente oficial.** Bases: "Asistente que traduce proyectos de ley o documentos públicos a lenguaje claro, citando siempre la fuente oficial". En el prototipo: Explícame.
2. **Contrastar lo que circula con el texto oficial.** Bases: "Herramienta de apoyo a la verificación de contenidos sospechosos". En el prototipo: Verifica esto.
3. **Saber a quién preguntar cuando el documento no responde.** Bases: que la ciudadanía "acceda a información pública verificable". En el prototipo: Pregúntale al Estado.

### Restricciones identificadas

| Tipo | Restricción | Fuente |
|---|---|---|
| Tiempo | Jornada del 6 de noviembre, de 08:30 a 18:45. Se evalúa la versión congelada al cierre técnico (14:45). Pitch de 5 minutos con demo y 3 de preguntas. | Bases §3 y §12 |
| Datos disponibles | Un documento oficial precargado: la Ley 21.801, PDF de la BCN de 4 páginas. Las bases sugieren datos abiertos del Congreso, SERVEL, Consejo para la Transparencia, datos.gob.cl y presupuestos municipales; las APIs que funcionan están en `APIS-DATOS-ABIERTOS-CHILE.md`. | `README.md`; Bases, Desafío 3 |
| Tecnología | App en Streamlit (Python 3.11 o superior). Modelo de IA intercambiable (Anthropic, OpenAI o Google) desde `.env`. Sin base de datos ni login. Sin base vectorial: el documento completo va en el contexto del modelo. Cada equipo usa sus propios notebooks. | `README.md`; Bases §11 |
| Normativa | Restricciones éticas y nota para la demostración del Desafío 3. No usar datos sensibles reales sin resguardo y consentimiento explícito. Checklist ético como requisito de admisibilidad. Falta confirmar en la BCN qué ley de datos personales aplica. | Bases; #25 |
| Presupuesto | La organización entrega cuentas para herramientas de IA. Límite de uso: 20 consultas cada 10 minutos por persona y 30 por minuto para toda la app. Costo por pregunta: sin calcular. Riesgo de que el modelo gratuito se quede sin tokens. | Bases §11; `core/limites.py`; #20; #30 |

## Lista de verificación

- [ ] Todos los integrantes leyeron el desafío (sin registro)
- [x] Identificamos al menos 3 actores (en esta ficha)
- [x] Separamos hechos de supuestos (en "¿Qué sabemos y qué estamos suponiendo?")
- [ ] Acordamos las 3 necesidades prioritarias (hay una propuesta; falta acordarla)

*Consejo: roten roles entre los 5: tiempo, registro, voz ante el mentor, apoyo técnico y control de calidad.*

---

*Hackathon IA Aplicada | Duoc UC - Pontificia Universidad Católica de Chile | Etapa 1: Inmersión | Equipo*
