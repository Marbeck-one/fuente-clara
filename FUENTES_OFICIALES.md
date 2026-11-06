# Fuentes oficiales · Fuente Clara

Lista de documentos cargados en `data/documentos/` y registrados en `data/documentos/catalogo.yaml`, con su criterio de inclusión y la verificación hecha contra la fuente oficial.

## Criterios de inclusión

Un documento se carga solo si cumple los cuatro criterios:

1. **Emisor oficial:** lo publica un organismo del Estado (BCN Ley Chile, Diario Oficial, Cámara, Senado, Mineduc, etc.).
2. **Versión con fecha:** el ejemplar declara su fecha de versión o de última modificación.
3. **Enlace permanente:** existe una URL oficial estable que permite volver a la fuente.
4. **Texto legible:** el PDF trae texto seleccionable, no es un escaneo ni una imagen.

Si un documento no cumple alguno, no se carga. Tampoco se usan copias de terceros ni resúmenes: siempre el texto oficial.

## Verificación

Método aplicado el **06-11-2026** por Maximiliano Correa (Psychosaur):

- Se abrió cada `fuente_url` y se comprobó que responde **200**.
- Se comparó la fecha de versión declarada en el catálogo con el `idVersion` de la URL oficial de BCN.
- Las 9 fuentes calzan en fecha y norma. Todas tienen cabecera `%PDF-` válida.

## Documentos cargados

| # | Norma | Archivo | Emisor / versión | Enlace oficial |
|---|---|---|---|---|
| 1 | Ley 21.801 · Prohíbe y regula el uso de celulares en los colegios | `ley_21801_celulares_en_colegios.pdf` | BCN Ley Chile · 11-feb-2026 | https://bcn.cl/122kkM |
| 2 | Ley 19.628 · Protección de la vida privada (datos personales) | `LEY-19628_28-AGO-1999.pdf` | BCN Ley Chile · 09-may-2023 | https://bcn.cl/3a0ih |
| 3 | Ley 19.880 · Bases de los procedimientos administrativos | `LEY-19880_29-MAY-2003.pdf` | BCN Ley Chile · 01-nov-2026 | https://bcn.cl/pYxskj |
| 4 | Ley 20.285 · Acceso a la información pública | `LEY-20285_20-AGO-2008.pdf` | BCN Ley Chile · 11-jul-2025 | https://bcn.cl/gPKjtt |
| 5 | Ley 20.720 · Reorganización y liquidación de empresas y personas | `Ley-20720_09-ENE-2014.pdf` | BCN Ley Chile · 30-dic-2023 | https://bcn.cl/3l2cz |
| 6 | Ley 21.643 · Ley Karin (acoso laboral, sexual y violencia en el trabajo) | `Ley-21643_15-ENE-2024.pdf` | BCN Ley Chile · 03-ene-2025 | https://bcn.cl/yRoHSk |
| 7 | Ley 21.663 · Ley marco de ciberseguridad | `Ley-21663_08-ABR-2024.pdf` | BCN Ley Chile · 01-mar-2025 | https://bcn.cl/ZuSFox |
| 8 | Ley 19.496 · Protección de los derechos de los consumidores (DFL 3 de 2019) | `Decreto-con Fuerza de Ley-3_31-MAY-2021.pdf` | BCN Ley Chile · 11-jul-2025 | https://bcn.cl/sG7L2q |
| 9 | Ley 18.603 · Orgánica constitucional de los partidos políticos (DFL 4 de 2017) | `Decreto-con Fuerza de Ley-4_06-SEP-2017.pdf` | BCN Ley Chile · 16-feb-2021 | https://bcn.cl/3ldan |

`EJEMPLO_FICTICIO_tarjeta_muevete.txt` no es una fuente oficial: está marcado `ficticio: true` y solo sirve para desarrollo.

## Mantención

- Las leyes 19.628, 20.285 y 19.496 (DFL 3) declaran **Fin Vigencia: 30-NOV-2026** en el encabezado del PDF. Después de esa fecha hay que bajar la versión nueva y repetir la verificación.
- Al agregar una fuente: descargar el PDF oficial, registrarlo en `catalogo.yaml` con `titulo`, `fuente_nombre`, `fuente_url` y `trata_de`, y anotarlo en esta tabla.

## Candidatas para la siguiente etapa

Estas fuentes están identificadas pero todavía no se cargan porque no entregan un PDF con versión fechada y enlace permanente, o falta descargarlas y validarlas:

- Cámara de Diputadas y Diputados (proyectos y votaciones).
- Senado (tramitación de proyectos).
- Diario Oficial (publicación de normas).
- Portal de Transparencia.
- Mineduc (normativa educativa).
