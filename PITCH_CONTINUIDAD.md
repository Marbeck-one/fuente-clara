# Continuidad · Fuente Clara (P15)

> Borrador para la diapositiva y el párrafo del pitch (P16).
> Los campos `[COMPLETAR]` son datos que todavía no tenemos y las cifras marcadas **SUPUESTO** no están confirmadas.

## 1. Diapositiva sugerida

**Título:** Fuente Clara después del hackathon

- **Quién lo usa:** estudiantes, apoderados y docentes que necesitan entender una ley sin leer el texto completo. Primer foco: colegios, con la Ley 21.801.
- **Quién lo paga o apoya:** `[COMPLETAR: modelo de financiamiento acordado]`. Propuesta del equipo, aún sin confirmar: Fundación Padre Hurtado, colegios y municipios.
- **Cuánto cuesta:** el costo por pregunta es `[COMPLETAR]` y la mantención mensual estimada es `[SUPUESTO]`.
- **Escalar es barato:** se agrega un PDF al catálogo, no se reescribe el sistema. Hoy hay 9 leyes oficiales cargadas.
- **Próximos pasos:** ampliar fuentes y accesibilidad, sumar analítica y decidir los módulos nuevos (ver sección 5).

## 2. Párrafo de continuidad

Fuente Clara está pensada para estudiantes, apoderados y docentes que necesitan entender qué dice una ley sin leer el texto completo. El sistema ya funciona sobre cualquier documento oficial: hoy tiene nueve leyes cargadas y sumar una nueva es cargar el PDF y registrarlo en el catálogo, sin reescribir la app. Para continuar después del hackathon buscamos un socio que lo adopte —la propuesta es la Fundación Padre Hurtado, colegios y municipios— y financiamiento para cubrir hosting y API. El costo por pregunta es `[COMPLETAR]` y la mantención mensual estimada es `[SUPUESTO]`. Los próximos pasos son ampliar fuentes, accesibilidad y analítica, y decidir los módulos nuevos de contratos, programas de gobierno y Clave Única.

## 3. Costo por pregunta

Medición real del repositorio con la Ley 21.801 (el documento de la demo):

| Concepto | Caracteres | Tokens aprox. (caracteres / 4) |
|---|---|---|
| Documento completo en el prompt | 13.775 | 3.443 |
| Prompt del filtro | 2.007 | 501 |
| Prompt de Explícame | 2.104 | 526 |
| **Entrada de una pregunta normal** (2 llamadas: filtro + explicación) | — | **7.913** |

- Una pregunta normal hace **2 llamadas** al modelo y envía el documento completo en cada una.
- Un intento de manipulación rechazado por el guardrail hace **0 llamadas**.
- Las preguntas tendenciosas o fuera del documento hacen **1 llamada** (solo el filtro).

**Fórmula del costo:**

```
costo por pregunta normal = (7.913 × precio_entrada + tokens_salida × precio_salida) / 1.000.000
```

- `precio_entrada` y `precio_salida`: `[COMPLETAR: dato de Becker, precio por 1M de tokens del modelo de la demo]`.
- `tokens_salida`: **600 SUPUESTO** (pendiente de confirmar).

Sin el precio del modelo no hay un monto: no lo inventamos.

## 4. Mantención mensual

Cifras de referencia, todas marcadas como supuesto hasta confirmarlas:

| Ítem | Valor | Estado |
|---|---|---|
| Hosting | US$0 con el plan gratuito de Streamlit Community Cloud | **SUPUESTO**, verificar límites |
| Dominio | ~US$12 al año (~US$1 al mes) | **SUPUESTO** |
| API | costo por pregunta × consultas al mes | **FÓRMULA**; falta el precio |
| Horas de equipo | `[COMPLETAR]` | PENDIENTE |

## 5. Próximos pasos (issues abiertos)

### Próximos pasos

- #2 · P2a · Más documentos oficiales y filtro por tema (ej. herencia)
- #4 · P3a · Verifica esto: leer una captura de pantalla
- #6 · P3c · Dictar la pregunta por micrófono
- #7 · P4 · Análisis de contratos (módulo nuevo)
- #9 · P6 · Unificador de reportes de programas de gobierno
- #10 · P7 · Contrasta tu programa: verificar una afirmación contra un programa de gobierno
- #11 · P8 · Clave Única para opinar sobre proyectos de ley
- #27 · P22 · Analítica por perfil
- #29 · Guardrail: segunda revisión de cada respuesta con una IA «jueza»
- #30 · Model routing: elegir el modelo según la tarea

### Decisión de equipo

Estos cuatro también aparecen arriba, pero necesitan una decisión antes de implementarse:

- #7 · P4 · Análisis de contratos (módulo nuevo)
- #9 · P6 · Unificador de reportes de programas de gobierno
- #10 · P7 · Contrasta tu programa
- #11 · P8 · Clave Única

### Ya cerrado

- #15 · P11 · Más fuentes oficiales para verificar: 9 fuentes cargadas y verificadas en `FUENTES_OFICIALES.md`.

## 6. Datos pendientes para cerrar esta diapositiva

1. Precio de entrada y salida por 1M de tokens del modelo de la demo.
2. Confirmar los 600 tokens de salida promedio o reemplazarlos por el dato real.
3. Modelo de financiamiento y estado real del socio (Fundación Padre Hurtado, colegios o municipios).
4. Horas de mantención mensual y costo de API estimado para un volumen de consultas.
