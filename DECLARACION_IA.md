# Declaración de transparencia sobre el uso de IA · Fuente Clara

> Plantilla. Completar los campos `___` antes del cierre técnico (14:45).

## 1. Modelo y proveedor

| Uso en la app | Proveedor | Modelo | Dónde se configura |
|---|---|---|---|
| Filtro de alcance, Explícame, Verifica esto y Pregúntale al Estado | Anthropic | `claude-sonnet-5-5`; si falla o se satura, responde `claude-haiku-5-5` | `LLM_PROVIDER`, `LLM_MODEL` y `LLM_CADENA` en `.env` |
| Lectura de capturas en Verifica esto | Mismo proveedor activo | Mismo modelo | La captura viaja solo al proveedor activo; no se guarda |

Se usa el mismo modelo para las cuatro tareas. La app muestra en pantalla qué modelo está activo, y bajo cada respuesta, el modelo que la generó.

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
- **Guardrail** (`core/guardrail.py`): antes de la IA se rechazan los intentos típicos de manipulación y las entradas demasiado largas; el texto de la persona va entre marcas y las reglas dicen que es dato, no instrucción; después de la IA, una respuesta que opina, da un veredicto ("verdadero", "falso") o muestra las instrucciones internas no se muestra, y se le quitan enlaces e imágenes.
- **Borrador armado con plantilla** (`config/transparencia.yaml`) con marcadores `[TU NOMBRE]` y `[TU DIRECCIÓN]`.
- **Nada exige una cuenta.** La cuenta es opcional y por defecto está desactivada (ver sección 5d). Lo que escribe la persona no se guarda, salvo que lo autorice al votar 👎 una respuesta (ver sección 5b).
- **Trazabilidad** (`core/votos.py`): cada voto guarda el modelo y la versión de las instrucciones (`prompts.VERSION`, cambia sola al editar un prompt), para saber si un cambio mejoró o empeoró las respuestas. Panel público en la página «Calidad de las respuestas».

## 5. Datos que se envían al proveedor de IA

En cada consulta se envía el documento público completo y el texto que escribió la persona. No se envían datos de identificación porque la app no los pide.
Política de retención de datos del proveedor elegido (Anthropic, API comercial):
- Borra automáticamente las entradas y salidas de la API dentro de 30 días. Las guarda más tiempo solo si su sistema las marca por infringir su política de uso (hasta 2 años) o si la ley lo exige. Fuente: «How long do you store my organization's data?», https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data (actualizada el 01-07-2026).
- No usa las entradas ni las salidas de la API para entrenar sus modelos. Fuentes: https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training y Commercial Terms, sección B (https://www.anthropic.com/legal/commercial-terms).
- Los votos 👍/👎 de Fuente Clara se guardan en el servidor del equipo y no se envían a Anthropic.

## 5b. Votos sobre las respuestas

- Bajo cada respuesta la persona puede votar 👍 o 👎. Cada voto guarda solo su contexto: pestaña, perfil, cuántas citas se verificaron, modelo, versión de las instrucciones y fecha. **Nunca la pregunta ni la respuesta.**
- Si vota 👎, puede elegir un motivo de una lista fija (sin texto libre) y, **solo si marca la casilla**, autorizar que se guarden su pregunta y la respuesta "para mejorar las respuestas del modelo". La app no entrena ningún modelo: con esas respuestas el equipo corrige las instrucciones.
- Antes de guardar se ocultan RUT, correos y teléfonos. El archivo (`data/votos/`) está fuera del repositorio y solo el equipo lo lee, con una clave (`CLAVE_EQUIPO`).
- Retención de las respuestas guardadas: **90 días** desde que la persona autoriza el guardado; después se eliminan.

## 5c. Voz: escuchar y dictar

- **Escuchar la respuesta:** usa la voz del propio navegador (`speechSynthesis`). Fuente Clara no envía el texto a ningún servicio de voz ni a la IA, y no guarda audio. Según el dispositivo, la voz del sistema puede ser de red; eso lo decide el navegador.
- **Dictar la pregunta:** usa el reconocimiento de voz del navegador (`SpeechRecognition`). **El audio sale del dispositivo**: en Chrome lo procesa el servicio de voz de Google (en otros navegadores, el de su fabricante). Fuente Clara no recibe ni guarda el audio; solo recibe el texto transcrito, que la persona revisa antes de enviar, y desde ahí sigue el mismo camino que un texto escrito (sección 5). El botón nunca escucha solo y la pantalla avisa de este envío.

## 5d. Cuenta opcional

- **Estado actual:** se puede entrar con Google en local, probado el 06-11-2026 con una cuenta. A Google solo se le pide la identidad (`scope=openid`), no el correo ni el nombre. También existe un modo demostración (`AUTH_MOCK=1`), que simula el login, no contacta a ningún proveedor y lo avisa en pantalla. Sin esta configuración no hay login.
- **Para qué sirve:** subir el tope de 5 a 20 consultas cada 10 minutos y medir el uso. Sin cuenta se puede usar toda la app.
- **Qué se guarda:** un identificador seudónimo, fechas de ingreso y conteos de consultas por día y módulo. Las consultas sin cuenta se suman sin distinguir personas. Nunca correo, nombre, tokens ni lo que la persona escribe, y los votos no se ligan a la cuenta. El identificador seudónimo sigue siendo un dato personal: solo se puede ligar a alguien con el secreto y los datos del proveedor.
- **Retención:** se elimina tras 90 días sin uso, o al momento con el botón «Borrar mis datos».

## 6. IA usada para construir el prototipo

- Asistente de código: Claude Code (Anthropic), usado para generar la estructura inicial del proyecto. El equipo revisó y ajustó: ___
- Otras herramientas: ___

## 7. Limitaciones conocidas

- La verificación comprueba que el texto citado existe en el documento, no que la explicación sea correcta. Por eso la cita siempre se muestra para que la persona la lea.
- El filtro puede equivocarse con preguntas ambiguas. Resultado medido con `scripts/evaluar.py` el 06-11-2026 (Ley 21.801, `claude-sonnet-5-5`, instrucciones `v-5a9f5c8`):
  - **Explícame:** acertó en los 37 casos. Las 6 preguntas normales tuvieron cita verificada; detectó las 5 del tema sin el dato y las 3 de otro tema; rechazó las 3 tendenciosas y los 20 intentos de manipulación.
  - **Verifica esto:** 5 de 5 afirmaciones con la etiqueta esperada.
  - **Pregúntale al Estado:** 5 de 5 borradores, con un organismo razonable según la revisión del equipo.
  - **Tiempo:** una respuesta completa de Explícame tarda 10,8 s en promedio (máximo 13,7 s); Verifica esto, 9,6 s; Pregúntale al Estado, 8,0 s.
  - **Alcance:** es un set chico y una sola corrida, así que no asegura que acierte con otras preguntas. Los 20 intentos de manipulación los frenaron las reglas fijas antes de llegar a la IA: no miden qué hace la IA con un intento que esquive esas reglas.
- La extracción de texto de algunos PDF (escaneados o con columnas) puede fallar. Documento usado en la demo: Ley 21.801, PDF oficial de la BCN (https://bcn.cl/122kkM), con texto digital (no escaneado) y 4 páginas.