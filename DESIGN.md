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

## Pendientes

1. Validar que la paleta no se asocie a ninguna coalición política.
2. Probar con dos o tres personas mayores el tamaño de 17 px y las pestañas con ícono.
3. Selectores CSS sobre el DOM interno de Streamlit (`stTab`, `stExpander`, `stCode`): revisarlos si se actualiza Streamlit.
