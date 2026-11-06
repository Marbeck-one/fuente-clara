# Fuente Clara · Sistema de diseño

> Método tomado del sistema de diseño de PonleNota (capa de tokens, color con significado, 60/30/10, accesibilidad como requisito). Identidad propia.
> La numeración de secciones es estable: el código cita `DESIGN.md §N`. Lo nuevo se agrega al final.

## 1. Identidad

**Nombre:** Fuente Clara. Dice la promesa completa: la *fuente* oficial, dicha *clara*. También es agua: una fuente de agua clara, que se ve hasta el fondo.

**Debe transmitir:** claridad, neutralidad, trazabilidad, cercanía.

**Lo que la marca no es:** un verificador que reparte veredictos ni un actor político. Fuente Clara muestra lo que dice el texto y la persona decide. Una pantalla que insinúe "esto es verdad" o "esto es mentira" está mal, aunque se vea bien.

**Principio rector:** ¿esto ayuda a que una persona entienda qué dice el documento y de dónde sale, en menos de un minuto? Si no, el elemento sobra.

## 2. Dirección visual

Tres ejes: **sobriedad institucional** (la tinta) + **la marca del lector** (el resaltador) + **aire** (neutros slate).

Evitar: degradados, glassmorphism, sombras fuertes, colores saturados en superficies grandes y cualquier cosa que parezca propaganda o un medio partidista.

## 3. Paleta y tokens

Los colores viven en dos sitios y en ninguno más: `.streamlit/config.toml` (tema de Streamlit) y las variables `--fc-*` de `static/estilo.css`.

| Token | HEX | Rol | Contraste |
| --- | --- | --- | --- |
| `tinta` | `#083344` | Identidad: títulos, botón primario, logo, borde del texto oficial | 13,40:1 sobre blanco |
| `tinta-hover` | `#164E63` | Único uso: hover del primario | 9,11:1 con blanco |
| `accion` | `#0E7490` | Antetítulos, enlaces, anillo de foco | 5,36:1 sobre blanco |
| `resaltador` | `#FDE68A` | **Solo** fondo del texto literal citado | 14,33:1 con `slate-900` |
| `fondo` | `#F8FAFC` | Página (slate-50) | — |
| `superficie` | `#FFFFFF` | Tarjetas | — |
| `campo` | `#F1F5F9` | Campos de texto, lado "afirmación" (slate-100) | — |
| `texto` / `texto-2` / `texto-3` | `#0F172A` / `#475569` / `#64748B` | Principal / secundario / atenuado | 7,58:1 y 4,76:1 sobre blanco |
| `aviso` | `#9A3412` sobre `#FFF7ED` | Avisos: ejemplo ficticio, cita no encontrada, por verificar | 6,88:1 |

**60/30/10:** 60 % neutros slate, 30 % tinta, 10 % acción + resaltador.

La tinta petróleo se eligió también por estar lejos de los colores de partido más reconocibles. **Validarlo con el equipo** antes del pitch.

## 4. El color con significado

Ningún color decora y ninguno es la única vía de un mensaje: siempre hay texto o ícono que lo dobla.

1. **El color nunca da veredicto.** Las tres etiquetas del verificador ("＝ El texto lo respalda", "≠ El texto dice otra cosa", "∅ El texto no lo menciona") comparten la misma pastilla neutra. Se distinguen por símbolo y texto, nunca por rojo o verde.
2. **El amarillo es del documento.** El resaltador marca solo texto literal verificado. Por eso los avisos usan naranja y no amarillo: si el amarillo aparece en todas partes, deja de significar "esto lo dice el texto".
3. **Rojo solo para fallas del sistema** (la IA no respondió), nunca para contenido.
4. **Cian claro (`info`) para límites de la herramienta:** "Fuente Clara no opina", "El documento no responde esta pregunta".

## 5. Tipografía: dos voces

| Voz | Fuente | Uso |
| --- | --- | --- |
| Fuente Clara (explica) | **Atkinson Hyperlegible Next**, variable 200–800 | Toda la interfaz. Diseñada por el Braille Institute para baja visión: letras que no se confunden (I/l/1, O/0) |
| El documento (cita) | **Source Serif 4**, 400 | Solo el texto literal de las citas |

Regla: **serif + resaltador = palabras exactas del documento.** Nunca se usa serif para texto que escribió la IA.

Ambas autoalojadas en `static/fuentes/` (54 kB en total, subset latino, licencia OFL): ninguna petición a terceros. Cuerpo base de **17 px** (uno más que lo habitual) por lectores mayores y baja alfabetización digital.

Escala: título del documento 24 px / 800 · título de módulo 24 px / 800 · h3 18 px / 700 · antetítulo 13 px / 700, mayúsculas, `letter-spacing .08em`.

## 6. Logo

Una **gota** (fuente, agua clara) con tres líneas de texto dentro; la del medio va **resaltada en amarillo**: es la cita verificada, el mecanismo central del producto dibujado en el símbolo. Funciona a 16 px.

`static/logo.svg` (interfaz) y `static/favicon.svg` (con variante para pestañas oscuras). Logotipo: **Fuente** en 800 + Clara en 400, tinta, 20 px.

## 7. Componentes

- **Tarjeta del documento:** protagonista de la pantalla. Antetítulo "Estás leyendo", título, fuente oficial enlazada y pastillas (ejemplo ficticio, modelo de IA). La marca va arriba y en pequeño.
- **Encabezado de módulo:** antetítulo "Paso N · Verbo" + h2 + bajada. Mismo ritmo en los tres (`encabezado()` en `modulos/comun.py`).
- **Tarjetas:** blancas, borde slate-200, radio 12 px, `shadow-sm`. Siempre más claras que la página.
- **Pestañas:** tres columnas iguales, ícono arriba, 56 px de alto; la activa en tinta con barra de 3 px.
- **Cita:** expander con artículo, página y estado. Dentro, texto en serif con resaltador y borde izquierdo tinta. La cita no encontrada va tachada, con borde naranja y la nota "No lo tomes como cita".
- **Comparación:** "Lo que dice la afirmación" en `campo` (voz ajena) y "Lo que dice el texto oficial" en blanco con borde tinta. Lado a lado desde 480 px.
- **Recuadro de decisión:** borde de 2 px en tinta. Es el único contenedor con borde grueso, porque es el punto de decisión humana. El enlace al portal solo aparece tras marcar la confirmación.
- **Pie fijo:** símbolo de 16 px y la frase de alcance.

## 8. Espacio, radios, elevación y movimiento

- Múltiplos de 4 px. Ancho máximo de 46 rem.
- Radios: 8 px botones, 12 px tarjetas, completo en pastillas.
- Solo `shadow-sm`.
- Movimiento: los resultados entran desde 8 px abajo en 500 ms, animando solo `transform` y `opacity`. Con `prefers-reduced-motion` todo cae a 0.

## 9. Accesibilidad

Todos los pares de texto superan AA (tabla de §3). Objetivos táctiles de 44 px o más (pestañas 56). Foco visible de 2 px en `accion`. Nada se comunica solo con color.

## 10. Implementación en Streamlit

- **Regla 1:** se cambian tokens, no componentes. Primero `config.toml`; el CSS solo cubre lo que el tema no alcanza.
- `st.html` elimina las etiquetas `<style>` y `<svg>`: la hoja de estilos se inyecta con `st.markdown(..., unsafe_allow_html=True)` y el logo va como `<img>` desde `static/`.
- Para dar estilo a un contenedor se usa `key`: Streamlit agrega la clase `st-key-<key>`. Los contenedores `fc-tarjeta-*` reciben fondo, sombra y entrada animada.
- Todo texto dinámico que entra en HTML pasa por `html.escape`.

## 11. Bases de la competencia

Fuente: *Bases Oficiales · Hackathon de Inteligencia Artificial Aplicada · Congreso Social UC 2026 · v1* (Pontificia Universidad Católica de Chile y Duoc UC). El PDF original está en [`docs/Bases_Hackathon_IA_Congreso_Social_UC_2026.pdf`](docs/Bases_Hackathon_IA_Congreso_Social_UC_2026.pdf). Aquí va el texto de lo que afecta al diseño y a la evaluación. Los desafíos 1 y 2, la postulación, la premiación y la logística están solo en el PDF. Ante cualquier duda, manda el PDF.

### 11.1 Tema general: IA al servicio de la dignidad humana

«La pregunta de fondo no es solo qué puede hacer la IA, sino a quién sirve, cómo lo hace y qué lugar deja a la persona.» Toda propuesta debe demostrar que la tecnología está al servicio de las personas, y nunca al revés. Principios:

- **Dignidad ante todo:** la IA asiste, pero nunca sustituye el criterio ni el vínculo humano.
- **Impacto social verificable:** usuarios reales, indicadores y criterios de evaluación definidos desde el diseño.
- **Evaluación con criterio ético:** se valora el impacto social y la responsabilidad de la solución, no solo su sofisticación técnica.
- **Interdisciplinariedad real:** equipos mixtos UC y Duoc UC.
- **Acompañamiento pastoral integrado:** espacios de pausa y discernimiento que forman parte del proceso.
- **Innovación abierta:** prototipos y aprendizajes documentados y disponibles para la comunidad.

El impacto social y la ética suman el **50 %** de la evaluación final.

### 11.2 Antecedentes

Viernes 6 de noviembre de 2026, de 08:30 a 18:45 h, presencial en Duoc UC sede San Joaquín. 100 estudiantes (50 UC y 50 Duoc UC) en 20 equipos de 5. La premiación es el martes 10 de noviembre de 2026, en el Congreso Social UC.

### 11.3 Desafío 3 · Democracia: «Ciudadanía informada: IA contra la desinformación y para la participación cívica»

**Contexto:** la circulación de desinformación en redes sociales y mensajería, los contenidos generados por IA (deepfakes, textos sintéticos) y la desconfianza en las instituciones afectan la calidad del debate público. A la vez, muchas personas, en especial jóvenes, no entienden cómo funcionan los procesos legislativos, presupuestarios o electorales, ni cómo participar más allá del voto.

**Pregunta desafío:** ¿Cómo podríamos usar IA para que la ciudadanía acceda a información pública verificable, comprenda propuestas legislativas o programas de gobierno y participe en decisiones locales, fortaleciendo la confianza democrática en lugar de polarizarla?

**Usuarios y beneficiarios:** votantes jóvenes, organizaciones de la sociedad civil, municipios, medios locales y establecimientos educacionales (formación ciudadana), entre otros.

**Alcance esperado (líneas posibles):**
- Asistente que traduce proyectos de ley o documentos públicos a lenguaje claro, citando siempre la fuente oficial.
- Herramienta de apoyo a la verificación de contenidos sospechosos.
- Plataforma de participación local que sintetice opiniones ciudadanas de forma transparente.

**Datos sugeridos:** datos abiertos del Congreso (Cámara y Senado), SERVEL, Consejo para la Transparencia, datos.gob.cl y presupuestos municipales.

**Restricciones éticas:** neutralidad política verificable, trazabilidad de fuentes, no generación de contenido persuasivo partidista y mecanismos para evitar que la herramienta se use para manipular.

**Nota para la demostración:** «Dado el riesgo de que un resumen generado en vivo resulte sesgado o inexacto frente al jurado, en este desafío la demostración durante el pitch deberá realizarse exclusivamente sobre documentos públicos precargados y verificados previamente por el equipo (por ejemplo, proyectos de ley o presupuestos municipales específicos), identificando en pantalla la fuente oficial de cada respuesta. No se aceptarán demostraciones sobre consultas abiertas de actualidad política ni sobre candidaturas, partidos o personas en ejercicio de cargos públicos.»

### 11.4 Entregables de cada equipo

- Un **prototipo funcional (MVP)** apoyado por IA, en el que la IA aporte valor real y no sea decorativa.
- Una **presentación tipo pitch con demostración**, para explicar, argumentar y defender la propuesta ante el jurado.
- Una **declaración de transparencia** que indique qué modelos y herramientas de IA se usaron y de qué forma (en este repo: `DECLARACION_IA.md`).
- El **checklist ético** de la hackathon, completado en los checkpoints definidos (en este repo: `CHECKLIST_ETICO.md`).

Mínimo 2 sesiones de mentoría por equipo.

### 11.5 Agenda de la jornada

| Hora | Etapa | Descripción |
| --- | --- | --- |
| 08:30–09:30 | Acreditación e instalación | Registro, validación de equipos, revisión de dispositivos e instalación técnica |
| 09:30–10:00 | Ceremonia de inicio | Bienvenida, objetivos, desafíos, metodología, reglas y criterios de evaluación |
| 10:00–10:45 | Etapa 1 · Inmersión | Análisis del desafío: necesidades, actores y restricciones |
| 10:45–11:15 | Etapa 2 · Definición | Delimitación del problema, objetivo y alcance de la propuesta |
| 11:15–11:45 | Etapa 3 · Diseño | Funcionalidades, arquitectura, tecnologías y experiencia de usuario |
| 11:45–12:45 | Etapa 4 · Desarrollo | Construcción del prototipo y sus componentes principales |
| 12:45–13:30 | Almuerzo | Pausa de la competencia |
| 13:30–14:15 | Etapa 5 · Integración | Integración de componentes y pruebas de funcionamiento |
| 14:15–14:45 | Etapa 6 · Cierre técnico | Últimos ajustes |
| 14:45–16:15 | Etapa 7 · Preparación del pitch | Problema, solución, propuesta de valor y demo |
| 16:15–18:15 | Etapa 8 · Presentación final | Pitch y demostración ante el jurado, con ronda de preguntas |
| 18:15–18:35 | Evaluación | El jurado consolida los resultados y entrega veredicto sellado |
| 18:35–18:45 | Cierre | Cierre oficial de la jornada |

Metodología: Design Thinking, Google Design Sprint, Lean Startup, Open Innovation e IA Responsable como eje transversal. La organización puede ajustar los horarios y lo avisa a los equipos.

### 11.6 Ética e IA responsable

La ética es un eje transversal, no un módulo aparte. Todas las soluciones deben respetar:

- **Transparencia:** los equipos documentan qué modelos de IA usaron y cómo.
- **No discriminación:** revisión activa de sesgos en los datos y en los resultados generados.
- **Protección de datos:** ningún dato sensible real de personas se usa sin resguardo; se privilegian datasets sintéticos o públicos.
- **Dignidad de la persona:** la IA asiste; nunca sustituye el criterio ni el vínculo humano.
- **Supervisión humana:** toda solución mantiene un punto de decisión humana explícito.
- **Discernimiento comunitario:** dos checkpoints éticos durante la jornada, guiados por Pastoral, cuyo checklist forma parte de la evaluación.

### 11.7 Evaluación

Instancia única: el pitch con demostración, entre las 16:15 y las 18:15 h. **Se evalúa la versión del prototipo congelada al cierre técnico (14:45 h); los cambios posteriores no se consideran.**

- **Formato:** 1 o 2 representantes por equipo; 5 minutos de pitch con demo y 3 minutos de preguntas del jurado.
- **Jurado mixto:** académicos de la UC y de Duoc UC, Pastoral, e industria u organizaciones sociales.
- **Rúbrica única** para todos los equipos, con retroalimentación escrita.

| Criterio | Descripción | Peso |
| --- | --- | --- |
| Comprensión del problema y del usuario | Profundidad en el entendimiento del desafío, del contexto y del usuario real; problema bien delimitado y validado con evidencia o datos | 10 % |
| Uso pertinente de la IA (no decorativo) | La IA resuelve una parte central del problema y su aporte se justifica frente a alternativas sin IA; elección adecuada de modelos y técnicas | 15 % |
| Factibilidad técnica y calidad del prototipo | Prototipo funcional y demostrable, con arquitectura coherente, uso adecuado de datos y adaptación al usuario (p. ej., baja alfabetización digital) | 15 % |
| Ética, privacidad y mitigación de sesgos | Cumplimiento de las restricciones éticas del desafío, protección de datos, mitigación de sesgos, transparencia y punto de decisión humana explícito (checklist ético) | 25 % |
| Impacto y escalabilidad | Beneficio social verificable para los usuarios, modelo de operación realista y potencial de adopción, continuidad o escalamiento | 25 % |
| Calidad del pitch | Claridad, síntesis y solidez de la argumentación; demostración efectiva y respuesta a las preguntas del jurado | 10 % |

**Evaluación ética del pitch:**
- **Requisito de admisibilidad:** el checklist ético, completado y validado en los dos checkpoints, es condición para ser evaluado. Los equipos que no lo presenten completo al cierre técnico (14:45 h) no son evaluados ni pueden optar a las distinciones.
- **Calidad de la respuesta ética:** el criterio de 25 % evalúa la pertinencia de las medidas frente a las restricciones del desafío, la mitigación efectiva de sesgos, la protección de datos y un punto de decisión humana **explícito y demostrado en el prototipo**.
- **Defensa ante el jurado:** al menos una pregunta sobre riesgos éticos o escenarios de mal uso, cuya respuesta cuenta en este criterio.

### 11.8 Condiciones generales que tocan al prototipo

- **Protección de datos:** no se pueden usar datos sensibles reales de personas sin resguardo y consentimiento explícito; se privilegian datasets sintéticos o públicos.
- **Autoría:** los prototipos son de autoría compartida del equipo, con uso académico e institucional de la UC y Duoc UC. Los equipos autorizan publicar una ficha resumen de la solución y sus aprendizajes.

Consultas: citt@duoc.cl

### 11.9 Cómo responde este diseño a las bases

| Exigencia de las bases | Dónde se cumple en el diseño |
| --- | --- |
| Neutralidad política verificable | §1 (no es un actor político ni reparte veredictos), §3 (paleta lejos de colores de partido), §4.1 (el color nunca da veredicto) |
| Trazabilidad: fuente oficial en pantalla en cada respuesta | §7 (tarjeta del documento con fuente enlazada, citas con artículo y página), §5 (serif + resaltador = texto literal) |
| Punto de decisión humana explícito y demostrado | §7 (recuadro de decisión con borde grueso; el enlace al portal aparece solo tras confirmar) |
| Adaptación a baja alfabetización digital | §5 (Atkinson Hyperlegible, cuerpo de 17 px), §9 (contraste AA, objetivos de 44 px, nada solo con color) |
| Transparencia sobre la IA | §7 (pastilla con el modelo de IA en la tarjeta del documento) y `DECLARACION_IA.md` |
| Mecanismos contra la manipulación | §4.4 (avisos de límite de la herramienta: «Fuente Clara no opina») |

## Pendientes

1. Validar que la paleta no se asocie a ninguna coalición política.
2. Probar con dos o tres personas mayores el tamaño de 17 px y las pestañas con ícono.
3. Selectores CSS sobre el DOM interno de Streamlit (`stTab`, `stExpander`, `stCode`): revisarlos si se actualiza Streamlit.
