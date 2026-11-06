# Checklist ético · Fuente Clara

> Plantilla. Es requisito de admisibilidad: debe estar completo y validado en los dos checkpoints antes de las 14:45.
> Los textos precargados describen lo que ya hace el prototipo. Completar los `___`.

| Dimensión | Cómo lo resolvemos | Dónde se ve en el prototipo |
|---|---|---|
| **Transparencia** | Declaramos modelo, proveedor y usos en `DECLARACION_IA.md`. Cada respuesta muestra sus citas con artículo y página, y la fuente oficial del documento. | Arriba: nombre del documento, fuente oficial y modelo activo. En cada respuesta: citas en desplegables. |
| **Sesgos** | El documento se explica igual para todos; el perfil solo agrega "qué cambia para ti" según lo que dice el texto. Probamos el filtro con preguntas informales y con faltas de ortografía para que no rechace a quien escribe distinto. Resultado con el modelo de la demo (`scripts/probar_sesgos.py`, 06-11-2026, #25): la misma pregunta con cada perfil y sin perfil se respondió en 8 de 8 casos con cita verificada y largo parecido (51 a 113 palabras); 9 de 9 preguntas escritas formal, informal («en q casos te dejan usar el cel en el cole?») o con faltas («selular», «colejio») se respondieron igual. El «qué cambia para ti» describe lo que dice la ley, sin valorarlo. Diferencia encontrada: a apoderados la IA a veces los trata de «usted» y a estudiantes de «tú». | Selector de perfil en "Explícame". Set de prueba en `tests/preguntas_prueba.json`. |
| **Protección de datos** | Sin base de datos ni login. Lo que escribe la persona vive en la sesión y se pierde al cerrar, salvo que autorice guardarlo al votar 👎 una respuesta; en ese caso se ocultan RUT, correos y teléfonos, y solo el equipo lo lee con una clave. Los votos guardan solo su contexto (pestaña, modelo, versión de instrucciones), nunca el texto. El borrador usa `[TU NOMBRE]` y `[TU DIRECCIÓN]`: esos datos se completan en el portal oficial. | Aviso "No escribas tu nombre ni otros datos personales aquí" y marcadores en el borrador. |
| **Supervisión humana** | La app no envía nada. La persona revisa el borrador, confirma que lo revisó y decide si lo envía en el Portal de Transparencia. El verificador no da veredictos: muestra los textos y la persona decide. | Pestaña "Pregúntale al Estado": aviso "Revisa el borrador. Tú decides si lo envías…" y casilla de confirmación antes del enlace al portal. |
| **Neutralidad** | Filtro de alcance antes de cada módulo, reglas de neutralidad en todos los prompts (`core/prompts.py`) y mensaje fijo de rechazo. Nunca se usan las palabras "verdadero", "falso", "fake" ni "mentira", y el color nunca da veredicto: las tres etiquetas del verificador tienen el mismo color neutro (`DESIGN.md` §4). | Probar en vivo una pregunta tendenciosa. Pie de página fijo: "Esta herramienta solo explica el documento cargado. No opina ni recomienda." |
| **Riesgos de mal uso** | Ver tabla siguiente. | — |

## Flujo de datos

Qué sale del dispositivo de la persona, quién lo recibe y qué se guarda (#25). Sale del código: `modulos/comun.py`, `core/llm.py`, `core/votos.py`, `core/limites.py` y `static/voz.js`.

```
Teléfono o computador de la persona
   │  texto (pregunta, afirmación o duda) · perfil elegido · captura, solo si la sube en «Verifica esto»
   ▼
Servidor de Fuente Clara (computador del equipo, Streamlit)
   │  documento público completo + texto de la persona + perfil (o la captura, para sacarle el texto)
   ▼
Anthropic: claude-sonnet-5-5 (si falla o se satura, claude-haiku-5-5)
   │  respuesta
   ▼
Servidor: verifica cada cita contra el documento y revisa la respuesta (guardrail) → pantalla de la persona
```

| Dato | ¿Sale del dispositivo? | Quién lo recibe | ¿Se guarda? |
|---|---|---|---|
| Texto que escribe la persona | Sí | Servidor del equipo y Anthropic | No: vive en la sesión y se borra al cerrarla. Solo si vota 👎 y marca la casilla se guarda 90 días, con RUT, correos y teléfonos ocultos, y lo lee solo el equipo con clave |
| Perfil elegido | Sí | Servidor y Anthropic | Solo como contexto del voto, si la persona vota |
| Voto 👍/👎 y motivo | Sí | Servidor | Sí, en `data/votos/` (fuera del repositorio): pestaña, perfil, citas verificadas, modelo, versión de las instrucciones y fecha. Nunca el texto |
| Captura de pantalla | Sí | Servidor y Anthropic, que lee el texto de la imagen. La persona revisa y corrige ese texto antes de comparar | No |
| Audio al dictar | Sí | El servicio de voz del navegador (Google, en Chrome). Fuente Clara no recibe el audio, solo el texto transcrito | No, en Fuente Clara |
| Texto leído en voz alta | No: lo lee la voz del navegador | — | No |
| Nombre, dirección, RUT | No: la app no los pide | — | — (se completan en el portal oficial) |
| Hora de cada consulta | — | Servidor, para el límite de uso | Solo en memoria, unos minutos |

- **Anthropic** borra las entradas y salidas de la API dentro de 30 días y no las usa para entrenar modelos (detalle y fuentes en `DECLARACION_IA.md` §5).
- **Errores:** la consola del servidor anota el error técnico, nunca el texto de la persona.

## Riesgos de mal uso

| Riesgo | Mitigación |
|---|---|
| Usar "Verifica esto" para "certificar" una cadena con un pantallazo | Las etiquetas solo describen el texto ("El texto lo respalda") y la pantalla muestra siempre la cita y la fuente. |
| Forzar a la IA a opinar o hacer propaganda | Filtro de alcance + reglas en los prompts. Medido con `scripts/evaluar.py` y el modelo de la demo: 100 % de tendenciosas rechazadas (3 de 3, #12). |
| Manipular a la IA con instrucciones escondidas en la pregunta ("ignora tus reglas", "actúa como…") | Guardrail en 3 capas (`core/guardrail.py`): reglas fijas que rechazan los intentos típicos sin llamar a la IA; el texto de la persona va entre marcas y se trata como dato; y antes de mostrar una respuesta se bloquea si la IA opinó, dio un veredicto o filtró sus instrucciones, y se le quitan los enlaces. Medido con `scripts/evaluar.py --tipo manipulacion` y el modelo de la demo: 100 % rechazados (20 de 20, #12). Los 20 los frenaron las reglas fijas antes de llegar a la IA. |
| Cargar un documento alterado como si fuera oficial | Solo se muestran documentos registrados en `catalogo.yaml` con su fuente oficial; el equipo los compara con la fuente antes de la demo. |
| Gastar la cuota de la API con consultas masivas | Límite de uso (`core/limites.py`): 20 consultas cada 10 minutos por persona y 30 por minuto para toda la app, configurables en `.env`. No se limita por IP porque en un evento todos comparten el mismo wifi. |
| Usar el módulo 3 para inundar organismos con solicitudes | La app no envía nada; cada solicitud la envía una persona identificada en el portal oficial. |
| Preguntas sobre autoridades, candidaturas o partidos | El filtro las clasifica como "opinión o política partidista" y responde con el mensaje fijo. |

## Restricciones éticas del Desafío 3

| Restricción de las bases | Cómo la cumplimos |
|---|---|
| Neutralidad política verificable | Set de preguntas tendenciosas + métrica de rechazo. Resultado con el modelo de la demo: 3 de 3 preguntas tendenciosas y 20 de 20 intentos de manipulación rechazados (`scripts/evaluar.py`, #12). |
| Trazabilidad de fuentes | Citas verificadas con artículo y página + enlace a la fuente oficial. Cada respuesta indica el modelo y la versión de las instrucciones, y los votos permiten medir su calidad en el panel «Calidad de las respuestas». |
| No generar contenido persuasivo partidista | Filtro + prompts. Prueba en vivo durante el pitch. |
| Mecanismos contra la manipulación | Sin veredictos, documentos solo del catálogo, la persona decide. |
| Demo solo sobre documentos precargados y verificados | Documento usado: Ley 21.801, PDF oficial de la BCN (https://bcn.cl/122kkM) · Verificado contra la fuente por: Maximiliano Correa (Psychosaur), el 06-11-2026 (`FUENTES_OFICIALES.md`). Los datos legales de «Pregúntale al Estado» se verificaron contra la Ley 20.285 y el Consejo para la Transparencia (`config/transparencia.yaml`). |

## Validación en checkpoints

| Checkpoint | Hora | Revisado por | Observaciones | Cambios realizados |
|---|---|---|---|---|
| 1 | ___ | ___ | ___ | ___ |
| 2 | ___ | ___ | ___ | ___ |
