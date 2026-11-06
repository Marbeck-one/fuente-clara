# Checklist ético · Fuente Clara

> Plantilla. Es requisito de admisibilidad: debe estar completo y validado en los dos checkpoints antes de las 14:45.
> Los textos precargados describen lo que ya hace el prototipo. Completar los `___`.

| Dimensión | Cómo lo resolvemos | Dónde se ve en el prototipo |
|---|---|---|
| **Transparencia** | Declaramos modelo, proveedor y usos en `DECLARACION_IA.md`. Cada respuesta muestra sus citas con artículo y página, y la fuente oficial del documento. | Arriba: nombre del documento, fuente oficial y modelo activo. En cada respuesta: citas en desplegables. |
| **Sesgos** | El documento se explica igual para todos; el perfil solo agrega "qué cambia para ti" según lo que dice el texto. Probamos el filtro con preguntas informales y con faltas de ortografía para que no rechace a quien escribe distinto. Resultado: ___ | Selector de perfil en "Explícame". Set de prueba en `tests/preguntas_prueba.json`. |
| **Protección de datos** | Sin base de datos ni login. Lo que escribe la persona vive en la sesión y se pierde al cerrar, salvo que autorice guardarlo al votar 👎 una respuesta; en ese caso se ocultan RUT, correos y teléfonos, y solo el equipo lo lee con una clave. Los votos guardan solo su contexto (pestaña, modelo, versión de instrucciones), nunca el texto. El borrador usa `[TU NOMBRE]` y `[TU DIRECCIÓN]`: esos datos se completan en el portal oficial. | Aviso "No escribas tu nombre ni otros datos personales aquí" y marcadores en el borrador. |
| **Supervisión humana** | La app no envía nada. La persona revisa el borrador, confirma que lo revisó y decide si lo envía en el Portal de Transparencia. El verificador no da veredictos: muestra los textos y la persona decide. | Pestaña "Pregúntale al Estado": aviso "Revisa el borrador. Tú decides si lo envías…" y casilla de confirmación antes del enlace al portal. |
| **Neutralidad** | Filtro de alcance antes de cada módulo, reglas de neutralidad en todos los prompts (`core/prompts.py`) y mensaje fijo de rechazo. Nunca se usan las palabras "verdadero", "falso", "fake" ni "mentira", y el color nunca da veredicto: las tres etiquetas del verificador tienen el mismo color neutro (`DESIGN.md` §4). | Probar en vivo una pregunta tendenciosa. Pie de página fijo: "Esta herramienta solo explica el documento cargado. No opina ni recomienda." |
| **Riesgos de mal uso** | Ver tabla siguiente. | — |

## Riesgos de mal uso

| Riesgo | Mitigación |
|---|---|
| Usar "Verifica esto" para "certificar" una cadena con un pantallazo | Las etiquetas solo describen el texto ("El texto lo respalda") y la pantalla muestra siempre la cita y la fuente. |
| Forzar a la IA a opinar o hacer propaganda | Filtro de alcance + reglas en los prompts. Medido con `scripts/evaluar.py`: ___ % de tendenciosas rechazadas. |
| Cargar un documento alterado como si fuera oficial | Solo se muestran documentos registrados en `catalogo.yaml` con su fuente oficial; el equipo los compara con la fuente antes de la demo. |
| Usar el módulo 3 para inundar organismos con solicitudes | La app no envía nada; cada solicitud la envía una persona identificada en el portal oficial. |
| Preguntas sobre autoridades, candidaturas o partidos | El filtro las clasifica como "opinión o política partidista" y responde con el mensaje fijo. |

## Restricciones éticas del Desafío 3

| Restricción de las bases | Cómo la cumplimos |
|---|---|
| Neutralidad política verificable | Set de preguntas tendenciosas + métrica de rechazo. Resultado: ___ |
| Trazabilidad de fuentes | Citas verificadas con artículo y página + enlace a la fuente oficial. Cada respuesta indica el modelo y la versión de las instrucciones, y los votos permiten medir su calidad en el panel «Calidad de las respuestas». |
| No generar contenido persuasivo partidista | Filtro + prompts. Prueba en vivo durante el pitch. |
| Mecanismos contra la manipulación | Sin veredictos, documentos solo del catálogo, la persona decide. |
| Demo solo sobre documentos precargados y verificados | Documento usado: Ley 21.801, PDF oficial de la BCN (https://bcn.cl/122kkM) · Verificado contra la fuente por: ___ |

## Validación en checkpoints

| Checkpoint | Hora | Revisado por | Observaciones | Cambios realizados |
|---|---|---|---|---|
| 1 | ___ | ___ | ___ | ___ |
| 2 | ___ | ___ | ___ | ___ |
