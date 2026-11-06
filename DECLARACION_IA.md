# Declaración de transparencia sobre el uso de IA · Fuente Clara

> Plantilla. Completar los campos `___` antes del cierre técnico (14:45).

## 1. Modelo y proveedor

| Uso en la app | Proveedor | Modelo | Dónde se configura |
|---|---|---|---|
| Filtro de alcance, Explícame, Verifica esto y Pregúntale al Estado | ___ (anthropic / openai / google) | ___ | `LLM_PROVIDER` y `LLM_MODEL` en `.env` |

Se usa un solo modelo para las cuatro tareas. La app muestra en pantalla qué modelo está activo.

## 2. Para qué usamos IA

- **Filtro de alcance:** clasifica cada entrada como *dentro del documento*, *fuera del documento* u *opinión o política partidista*.
- **Explícame:** traduce el texto legal a lenguaje claro (nivel 8° básico) y explica qué establece el documento para un perfil (estudiante, trabajador/a, adulto mayor).
- **Verifica esto:** separa una cadena, post o titular en afirmaciones y ubica qué dice el texto oficial sobre cada una.
- **Pregúntale al Estado:** sugiere el organismo que podría tener la información y redacta el texto de la solicitud.

## 3. Qué NO hace la IA

- No responde con información externa al documento cargado.
- No opina, no evalúa, no recomienda cómo votar ni genera contenido persuasivo.
- No responde sobre candidaturas, partidos ni personas en cargos públicos.
- No dice si algo es "verdadero" o "falso". Las etiquetas del verificador las fija la app y solo describen lo que dice el texto.
- No genera datos jurídicos (ley, plazos, pasos, portal). Salen de `config/transparencia.yaml`, revisado por el equipo.
- No envía solicitudes ni toma decisiones. La persona revisa y decide.
- No pide nombre, dirección ni otros datos personales.

## 4. Controles que no dependen de la IA (están en el código)

- **Verificación de citas** (`core/citas.py`): cada cita se busca literalmente en el documento. La pantalla marca "Cita verificada" o "Cita no encontrada en el documento".
- **Respuestas sin cita verificada no se muestran** como válidas.
- **Etiquetas fijas** del verificador definidas en `modulos/verifica.py`.
- **Borrador armado con plantilla** (`config/transparencia.yaml`) con marcadores `[TU NOMBRE]` y `[TU DIRECCIÓN]`.
- **Sin base de datos ni login.** Lo que escribe la persona no se guarda, salvo que lo autorice al votar 👎 una respuesta (ver sección 5b).
- **Trazabilidad** (`core/votos.py`): cada voto guarda el modelo y la versión de las instrucciones (`prompts.VERSION`, cambia sola al editar un prompt), para saber si un cambio mejoró o empeoró las respuestas. Panel público en la página «Calidad de las respuestas».

## 5. Datos que se envían al proveedor de IA

En cada consulta se envía el documento público completo y el texto que escribió la persona. No se envían datos de identificación porque la app no los pide.
Política de retención de datos del proveedor elegido: ___

## 5b. Votos sobre las respuestas

- Bajo cada respuesta la persona puede votar 👍 o 👎. Cada voto guarda solo su contexto: pestaña, perfil, cuántas citas se verificaron, modelo, versión de las instrucciones y fecha. **Nunca la pregunta ni la respuesta.**
- Si vota 👎, puede elegir un motivo de una lista fija (sin texto libre) y, **solo si marca la casilla**, autorizar que se guarden su pregunta y la respuesta "para mejorar las respuestas del modelo". La app no entrena ningún modelo: con esas respuestas el equipo corrige las instrucciones.
- Antes de guardar se ocultan RUT, correos y teléfonos. El archivo (`data/votos/`) está fuera del repositorio y solo el equipo lo lee, con una clave (`CLAVE_EQUIPO`).
- Retención de las respuestas guardadas: ___

## 6. IA usada para construir el prototipo

- Asistente de código: Claude Code (Anthropic), usado para generar la estructura inicial del proyecto. El equipo revisó y ajustó: ___
- Otras herramientas: ___

## 7. Limitaciones conocidas

- La verificación comprueba que el texto citado existe en el documento, no que la explicación sea correcta. Por eso la cita siempre se muestra para que la persona la lea.
- El filtro puede equivocarse con preguntas ambiguas. Resultado medido con `scripts/evaluar.py`: ___
- La extracción de texto de algunos PDF (escaneados o con columnas) puede fallar. Documento usado en la demo: ___
