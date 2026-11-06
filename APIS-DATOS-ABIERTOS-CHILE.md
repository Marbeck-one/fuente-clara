---
titulo: APIs de datos abiertos de Chile que funcionan
verificado: 2026-11-06
metodo: llamadas reales con curl desde Linux
alcance:
  - Camara de Diputados (SOAP)
  - datos.gob.cl (CKAN)
  - Consejo para la Transparencia (CSV/XML + SPARQL + InfoLobby + InfoProbidad)
  - SINIM / presupuestos municipales (export SpreadsheetML)
  - BCN / Ley Chile (REST con API-KEY)
audiencia: agentes IA y desarrolladores
estado: operativo verificado
---

# APIs de datos abiertos de Chile que funcionan

> **Documento operativo, no exploratorio.** Solo contiene fuentes que respondieron correctamente
> en la verificacion del **2026-11-06**. Cada seccion indica que se puede obtener, que **no** se
> puede obtener, y las trampas concretas que rompen una integracion.

---

## 0. Reglas para un agente que use este documento

1. **No inventar endpoints.** Las unicas APIs confirmadas son las de las secciones 2 a 6.
2. **No asumir JSON.** La Camara habla SOAP/XML; el SINIM devuelve SpreadsheetML (XML de Excel).
3. **No asumir paginacion.** Solo CKAN (`datos.gob.cl`) tiene paginacion real.
4. **No asumir que un campo vacio significa error.** Varios metodos de la Camara devuelven
   `<Integrantes />` o `<Asistencia />` vacios de forma estructural (ver 2.8).
5. **No confundir identificadores.** El SINIM usa un `id` interno distinto del codigo legal de
   municipio (`id_legal`). Usar el equivocado devuelve la planilla sin filas de datos (ver 5.4).
6. **No consultar sin cache.** Ninguna de estas fuentes publica limites de tasa. Usar <= 1 req/s,
   `User-Agent` identificable y cache en disco.
7. **Si una fuente falla, no reintentar en bucle.** Senado y SERVEL no son APIs utilizables
   (ver seccion 7).

### 0.1 Matriz de decision

| Necesito... | Fuente | Seccion |
|---|---|---|
| Diputados, votaciones, sesiones, comisiones | Camara de Diputados (SOAP) | 2 |
| Descubrir datasets publicos del Estado | datos.gob.cl (CKAN) | 3 |
| Consultar datos tabulares ya indexados por CKAN | `datastore_search` | 3.5 |
| Casos y reclamos de transparencia | CPLT CSV/XML | 4.2 |
| Audiencias, viajes, donativos, lobbistas | InfoLobby CSV/Parquet o SPARQL | 4.4 |
| Declaraciones de patrimonio e intereses | InfoProbidad CSV o SPARQL | 4.5 |
| Presupuesto municipal, serie 2001-2025 | SINIM export | 5 |
| Texto de leyes y normas | BCN API v1 (requiere key) | 6 |

---

## 1. Convenciones de este documento

- **VERIFICADO**: se obtuvo una respuesta valida durante la verificacion.
- **NO VERIFICADO**: documentado por el proveedor pero no comprobado (requiere credencial).
- **NO DISPONIBLE**: se comprobo que no existe o no responde.
- Todas las URLs son absolutas y copiables.
- Los ejemplos usan `curl`; los snippets Python usan solo `requests` salvo que se indique.

---

## 2. Camara de Diputados - SOAP (VERIFICADO)

La mejor API del ecosistema: oficial, estable, sin autenticacion y sin costo.

### 2.1 Identidad del servicio

| Dato | Valor |
|---|---|
| Endpoint | `https://opendata.camara.cl/wscamaradiputados.asmx` |
| WSDL | `https://opendata.camara.cl/wscamaradiputados.asmx?WSDL` |
| Protocolo | SOAP 1.1 / 1.2 |
| Formato | XML |
| Auth | Ninguna |
| Costo | Gratis |
| Namespace de los elementos | `http://tempuri.org/` |
| **SOAPAction** | `http://tempuri.org/<metodo>` |

### 2.2 Regla critica: el SOAPAction

El `SOAPAction` **debe** ser `http://tempuri.org/<metodo>`. El namespace que declara el WSDL
**no** sirve como SOAPAction. Si se usa el namespace del WSDL, el servidor rechaza la accion.

```
SOAPAction: "http://tempuri.org/getDiputados_Vigentes"
```

Ademas, el metodo debe ir en el body con `xmlns="http://tempuri.org/"`:

```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getDiputados_Vigentes xmlns="http://tempuri.org/"/>
  </soap:Body>
</soap:Envelope>
```

La respuesta siempre tiene la forma:

```xml
<soap:Body>
  <getDiputados_VigentesResponse xmlns="http://tempuri.org/">
    ...
  </getDiputados_VigentesResponse>
</soap:Body>
```

### 2.3 Plantilla `curl` reutilizable

```bash
soap() {
  local method="$1"; local inner="$2"
  curl -s --max-time 40 \
    'https://opendata.camara.cl/wscamaradiputados.asmx' \
    -H 'Content-Type: text/xml; charset=utf-8' \
    -H "SOAPAction: \"http://tempuri.org/${method}\"" \
    --data "<?xml version=\"1.0\" encoding=\"utf-8\"?>
<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
  <soap:Body><${method} xmlns=\"http://tempuri.org/\">${inner}</${method}></soap:Body>
</soap:Envelope>"
}

# Ejemplo: diputados vigentes
soap getDiputados_Vigentes ''
```

### 2.4 Catalogo de metodos

| Metodo | Parametro(s) | Estado | Devuelve |
|---|---|---|---|
| `getPeriodosLegislativos` | - | VERIFICADO | Lista de periodos (ID, fechas, nombre) |
| `getPeriodoLegislativoActual` | - | **ROTO** | `<PeriodoLegislativo xsi:nil="true"/>` |
| `getLegislaturaActual` | - | VERIFICADO | Legislatura vigente (ID 58) |
| `getLegislaturas` | - | VERIFICADO | Lista de legislaturas |
| `getDiputados_Vigentes` | - | VERIFICADO | 155 diputados en ejercicio |
| `getDiputados_Periodo` | `prmPeriodoID` (int) | VERIFICADO | Diputados de un periodo (ID 6 -> 123) |
| `getDiputados` | - | NO PROBADO | Nomina historica completa |
| `getVotaciones_Boletin` | `prmBoletin` (string) | VERIFICADO | Votaciones del boletin |
| `getVotacion_Detalle` | `prmVotacionID` (int) | VERIFICADO | Votacion + voto por diputado |
| `getComisiones_Vigentes` | - | VERIFICADO | Comisiones (sin integrantes) |
| `getSesiones` | `prmLegislaturaID` (int) | VERIFICADO | Sesiones de la legislatura |
| `getSesionDetalle` | `prmSesionID` (int) | PARCIAL | Sesion (asistencia vacia) |
| `getSesionBoletinXML` | `prmSesionID` (int) | **VACIO** | Sin contenido util |

### 2.5 Como se invoca cada metodo

```bash
# Periodos legislativos
soap getPeriodosLegislativos ''

# Legislatura actual -> <ID>58</ID>, periodo 2026-03-11 a 2030-03-10
soap getLegislaturaActual ''

# Diputados de un periodo (int)
soap getDiputados_Periodo '<prmPeriodoID>6</prmPeriodoID>'

# Votaciones de un boletin (string, sin sufijo)
soap getVotaciones_Boletin '<prmBoletin>8575</prmBoletin>'

# Detalle de una votacion (int, viene del campo ID de getVotaciones_Boletin)
soap getVotacion_Detalle '<prmVotacionID>17495</prmVotacionID>'

# Sesiones de la legislatura 58
soap getSesiones '<prmLegislaturaID>58</prmLegislaturaID>'

# Detalle de sesion
soap getSesionDetalle '<prmSesionID>4777</prmSesionID>'
```

### 2.6 Estructura de los datos

**`getDiputados_Vigentes`** (155 registros):

```xml
<Diputado>
  <DIPID>843</DIPID>
  <Nombre>René Manuel</Nombre>
  <Nombre2> </Nombre2>
  <Apellido_Paterno>García</Apellido_Paterno>
  <Apellido_Materno>García</Apellido_Materno>
  <Fecha_Nacimiento>1950-05-24T00:00:00</Fecha_Nacimiento>
  <Sexo Codigo="1">Masculino</Sexo>
  <Militancias_Periodos />
</Diputado>
```

**`getVotaciones_Boletin`**:

```xml
<Votacion>
  <ID>17495</ID>
  <Fecha>2012-12-12T14:41:03</Fecha>
  <Tipo Codigo="6">Única</Tipo>
  <Resultado Codigo="2">Rechazado</Resultado>
  <Quorum Codigo="10">2/3 Presentes</Quorum>
  <Sesion>
    <ID>2884</ID><Numero>111</Numero>
    <Fecha>2012-12-12T10:30:00</Fecha>
    <FechaTermino>0001-01-01T00:00:00</FechaTermino>
    <Tipo Codigo="60">Ordinaria</Tipo>
  </Sesion>
  <Boletin>8575-05</Boletin>
  <Articulo>Insistencia texto aprobado...</Articulo>
  <Tramite Codigo="5">OBSERVACIONES P. DE LA R.</Tramite>
  <Informe Codigo="4">INFORME OBSERVACIONES</Informe>
  <TotalAfirmativos>60</TotalAfirmativos>
  <TotalNegativos>46</TotalNegativos>
  <TotalAbstenciones>0</TotalAbstenciones>
  <TotalDispensados>0</TotalDispensados>
</Votacion>
```

**`getVotacion_Detalle`** agrega el voto individual:

```xml
<Votos>
  <Voto>
    <Diputado>
      <DIPID>802</DIPID>
      <Nombre>Sergio</Nombre>
      <Apellido_Paterno>Aguiló</Apellido_Paterno>
      <Apellido_Materno>Melo</Apellido_Materno>
    </Diputado>
    <Opcion Codigo="1">Afirmativo</Opcion>
  </Voto>
</Votos>
```

**`getSesiones`**:

```xml
<Sesion>
  <ID>4777</ID>
  <Numero>22</Numero>
  <Fecha>2026-05-12T10:00:53</Fecha>
  <FechaTermino>2026-05-12T13:48:20</FechaTermino>
  <Tipo Codigo="60">Ordinaria</Tipo>
  <Estado Codigo="1">Celebrada</Estado>
</Sesion>
```

**`getComisiones_Vigentes`**:

```xml
<Comision>
  <ID>411</ID>
  <Nombre>Salud</Nombre>
  <Nombre_Alias>Salud</Nombre_Alias>
  <Nombre_Web>Salud</Nombre_Web>
  <Tipo Codigo="2101">Permanente</Tipo>
  <Correo_Electronico>saludcam@congreso.cl</Correo_Electronico>
  <Telefono>+56-32-2505520</Telefono>
  <Fax>+56-32-250</Fax>
  <Fecha_Constitucion>2022-03-14T00:00:00</Fecha_Constitucion>
  <Integrantes />
</Comision>
```

Los atributos `Codigo` son catalogos numericos estables; el texto es la etiqueta legible.
Guardar ambos: el codigo sirve para filtrar, el texto para mostrar.

### 2.7 Que SI se puede obtener

- Nomina de diputados vigentes e historicos por periodo, con `DIPID` estable.
- Votaciones por boletin, con totales por sentido del voto.
- Voto individual por diputado (via `getVotacion_Detalle`).
- Sesiones por legislatura, con fecha, numero, tipo y estado.
- Comisiones vigentes con contacto y tipo.
- Serie de periodos legislativos y legislaturas.

### 2.8 Que NO se puede obtener

- **Datos del Senado.** Esta API es solo Camara.
- **Tramitacion completa de un proyecto.** Solo votaciones y sesiones; no el historial de tramites.
- **Asistencia a sesiones.** `getSesionDetalle` devuelve `<Asistencia />` vacio.
- **Integrantes de comisiones.** `getComisiones_Vigentes` devuelve `<Integrantes />` vacio.
- **Contenido de la sesion por boletin.** `getSesionBoletinXML` devuelve una respuesta vacia.
- **Periodo legislativo actual.** `getPeriodoLegislativoActual` devuelve `xsi:nil="true"`.
- **Busqueda por texto o filtros por fecha.** No hay parametros para eso; hay que traer y filtrar en cliente.
- **JSON.** Solo SOAP/XML.
- **Paginacion.** No existe; cada metodo devuelve el conjunto completo.

### 2.9 Snippet Python (sin dependencias SOAP)

```python
import re
import requests

URL = "https://opendata.camara.cl/wscamaradiputados.asmx"

def camara(method: str, inner: str = "") -> str:
    body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body><{method} xmlns="http://tempuri.org/">{inner}</{method}></soap:Body>
</soap:Envelope>"""
    r = requests.post(
        URL,
        data=body.encode("utf-8"),
        headers={
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f'"http://tempuri.org/{method}"',
        },
        timeout=40,
    )
    r.raise_for_status()
    return r.text

def diputados_vigentes():
    xml = camara("getDiputados_Vigentes")
    out = []
    for m in re.finditer(r"<Diputado>(.*?)</Diputado>", xml, re.S):
        b = m.group(1)
        def tag(t):
            x = re.search(rf"<{t}>(.*?)</{t}>", b, re.S)
            return x.group(1).strip() if x else None
        out.append({
            "dipid": int(tag("DIPID")),
            "nombre": " ".join(filter(None, [tag("Nombre"), tag("Nombre2"),
                                             tag("Apellido_Paterno"), tag("Apellido_Materno")])).strip(),
            "nacimiento": tag("Fecha_Nacimiento"),
        })
    return out

print(len(diputados_vigentes()))  # 155
```

---

## 3. datos.gob.cl - CKAN (VERIFICADO)

Catalogo nacional de datos abiertos sobre **CKAN 2.10.4**. API REST JSON estandar, sin key.

### 3.1 Identidad

| Dato | Valor |
|---|---|
| Base API | `https://datos.gob.cl/api/3/action` |
| Version | CKAN 2.10.4 |
| Formato | JSON |
| Auth | Ninguna |
| Costo | Gratis |
| Datasets | 3.164 (verificado con `package_search?rows=0`) |
| Organizaciones | 276 (verificado con `organization_list?all_fields=true`) |

### 3.2 Acciones disponibles

| Accion | Uso |
|---|---|
| `package_search` | Buscar datasets |
| `package_show` | Metadatos de un dataset por `id` o `name` |
| `resource_search` | Buscar recursos por campo |
| `organization_list` | Listar organismos |
| `organization_show` | Detalle de un organismo |
| `group_list` | Listar grupos/temas |
| `datastore_search` | Consultar filas de un recurso tabular |
| `datastore_search_sql` | **NO DISPONIBLE** en este portal |
| `help_show` | Ayuda y parametros de una accion |
| `status_show` | Version y extensiones del portal |

**Importante:** `datastore_search_sql` **no esta habilitado**. Intentarlo devuelve
`"Action name not known: datastore_search_sql"`. Usar solo `datastore_search` con filtros.

### 3.3 Busqueda de datasets

```bash
curl -s 'https://datos.gob.cl/api/3/action/package_search?q=presupuesto%20municipal&rows=5'
```

Respuesta:

```json
{
  "success": true,
  "result": {
    "count": 2,
    "results": [
      {
        "title": "PRESUPUESTO MUNICIPAL 2021",
        "name": "presupuesto-municipal-2021",
        "organization": {"title": "Municipalidad de Pelluhue"},
        "resources": [
          {"format": "PDF", "datastore_active": false, "id": "0fd98bf4-..."}
        ]
      }
    ]
  }
}
```

Parametros utiles de `package_search`:

| Parametro | Ejemplo | Nota |
|---|---|---|
| `q` | `presupuesto municipal` | Busqueda full-text |
| `rows` | `100` | Maximo practico 1000 |
| `start` | `0` | Offset de paginacion |
| `fq` | `organization:muni_antofagasta` | Filtro Solr |
| `sort` | `metadata_modified desc` | Orden |
| `rows=0` | - | Solo devuelve `count` (conteo barato) |

### 3.4 Metadatos de un dataset

```bash
curl -s 'https://datos.gob.cl/api/3/action/package_show?id=presupuesto-municipal-2021'
```

Campos relevantes por dataset: `title`, `name`, `notes`, `organization`, `tags`, `license_title`,
`license_url`, `metadata_modified`, `resources[]`.

Campos relevantes por recurso:

| Campo | Tipo | Uso |
|---|---|---|
| `id` | uuid | Clave para `datastore_search` y descarga |
| `name` | str | Nombre legible |
| `format` | str | `CSV`, `XLSX`, `PDF`, `ZIP`, ... |
| `url` | str | Descarga directa |
| `datastore_active` | bool | **Si es `false`, `datastore_search` no sirve** |
| `datastore_contains_all_records_of_source_file` | bool | Fiabilidad del indexado |
| `size` | int | Bytes (puede ser null) |
| `last_modified` | str | Frescura |

### 3.5 Consulta tabular (`datastore_search`)

```bash
curl -s 'https://datos.gob.cl/api/3/action/datastore_search?resource_id=e5c240e8-d752-4488-a95d-1f98a99f2c33&limit=2'
```

Respuesta:

```json
{
  "success": true,
  "result": {
    "total": 228005,
    "fields": [{"id": "Region", "type": "text"}, {"id": "Cobertura", "type": "text"}],
    "records": [{"_id": 1, "Region": "10 Los Lagos", "Programas": "Comerciales"}]
  }
}
```

Parametros verificados (segun `help_show`):

| Parametro | Ejemplo | Nota |
|---|---|---|
| `resource_id` | uuid | Obligatorio |
| `limit` | `100` | Default 100; maximo del portal 32000 |
| `offset` | `0` | Paginacion |
| `filters` | `{"Region":"10 Los Lagos"}` | JSON, igualdad exacta |
| `q` | `texto` o `{"campo":"texto"}` | Busqueda full-text |
| `fields` | `Region,Programas` | Proyeccion de columnas |
| `sort` | `Region asc,Cobertura desc` | Orden |
| `distinct` | `true` | Filas distintas |
| `include_total` | `true` | Default true |

Ejemplo con filtro y proyeccion:

```bash
curl -sG 'https://datos.gob.cl/api/3/action/datastore_search' \
  --data-urlencode 'resource_id=e5c240e8-d752-4488-a95d-1f98a99f2c33' \
  --data-urlencode 'filters={"Region":"10 Los Lagos"}' \
  --data-urlencode 'fields=Region,Programas' \
  --data-urlencode 'limit=2'
```

### 3.6 Que SI se puede obtener

- Catalogo completo de datasets y organismos.
- Metadatos, licencias, etiquetas y frescura.
- Descarga directa de cualquier recurso (`resources[].url`).
- Consulta paginada y filtrada de recursos con `datastore_active: true`.

### 3.7 Que NO se puede obtener

- **SQL arbitrario.** `datastore_search_sql` no existe en este portal.
- **Datos de recursos no indexados.** Si `datastore_active` es `false`, solo queda descargar el archivo.
- **Contenido de PDF/XLSX/ZIP** por API. Hay que descargar y parsear.
- **Garantia de esquema.** Cada organismo publica como quiere; los nombres de columna cambian.
- **Series temporales unificadas.** No hay un endpoint consolidado; hay que cruzar datasets.

### 3.8 Trampa: DataStore "activo" pero vacio

Un recurso puede tener `datastore_active: true` y aun asi devolver `total: 0` y
`fields: [{"id": "_id"}]`. Ocurre cuando el indexado fallo.

Regla: antes de usar un recurso, ejecutar `datastore_search?limit=1` y comprobar `total > 0`.
Si `total == 0`, descargar el archivo original desde `resources[].url`.

---

## 4. Consejo para la Transparencia (VERIFICADO)

El CPLT expone **tres cosas distintas**, que no deben confundirse:

1. Casos y reclamos: **archivos CSV/XML estaticos** (no API REST).
2. InfoLobby e InfoProbidad: **catalogos CSV/Parquet** + **endpoint SPARQL**.
3. Plataforma `datos.cplt.cl`: **Virtuoso SPARQL 1.1**.

### 4.1 Identidad

| Componente | URL base | Tipo |
|---|---|---|
| Casos | `https://consejotransparencia.cl/transparencia_activa/datoabierto/archivos/` | CSV/XML |
| Portal de datos | `https://datos.cplt.cl/sparql` | SPARQL 1.1 |
| InfoLobby catalogos | `https://datosinfolobby.cplt.cl/catalogos/` | CSV/Parquet/RAR |
| InfoLobby SPARQL | `http://datos.infolobby.cl/sparql` | SPARQL (HTTP, no HTTPS) |
| InfoProbidad catalogos | `https://datos.cplt.cl/catalogos/infoprobidad/` | CSV/JSON/XML |
| InfoProbidad SPARQL | `https://datos.cplt.cl/sparql` | SPARQL 1.1 |

Motor SPARQL: **Virtuoso 07.20.3217**.
Auth: ninguna. Costo: ninguno.

### 4.2 Casos y reclamos (CSV)

| Archivo | Tamano verificado | Estado |
|---|---|---|
| `casos.csv` | 22.241.935 bytes | OK |
| `casos.xml` | 124.975.352 bytes | OK |
| `estadosPorCaso.csv` | 28.996.218 bytes | OK |
| `estadosPorCaso.xml` | 224.023.072 bytes | OK |
| `motivosPorCaso.csv` | - | OK |
| `motivosPorCaso.xml` | 53.758.510 bytes | OK |
| `reclamados.csv` | - | OK |
| `reclamados.xml` | 40.144.426 bytes | OK |
| `reclamantes.csv` | - | **404 NO DISPONIBLE** |
| `reclamantes.xml` | - | **404 NO DISPONIBLE** |

URLs:

```bash
curl -O 'https://consejotransparencia.cl/transparencia_activa/datoabierto/archivos/casos.csv'
curl -O 'https://consejotransparencia.cl/transparencia_activa/datoabierto/archivos/estadosPorCaso.csv'
curl -O 'https://consejotransparencia.cl/transparencia_activa/datoabierto/archivos/motivosPorCaso.csv'
curl -O 'https://consejotransparencia.cl/transparencia_activa/datoabierto/archivos/reclamados.csv'
```

**Formato:** UTF-8 con BOM, separador `;`, campos entrecomillados cuando contienen `;`.

Esquemas verificados:

`casos.csv` (16 columnas):

```
idcaso;ano;rol;codigoOR;NombreOR;folioSAI;fechaRecepcionCPLT;iDLugarIngreso;
lugarIngreso;iDTipoCaso;tipoCaso;fechaSolInstitucion;fEchaRespuestaInst;
idEstadoWeb;estado;resumen
```

`estadosPorCaso.csv`:

```
idcaso;fechRegistro;idEstado;estado;activo
```

`motivosPorCaso.csv`:

```
idCaso;IdMotivo;Motivo
```

`reclamados.csv` (nota: la columna `IDInstitucion,` incluye una coma literal en el encabezado):

```
idcaso;IDInstitucion,;Institucion
```

Ejemplo de lectura robusta:

```python
import csv

with open("casos.csv", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f, delimiter=";")
    for i, row in enumerate(reader):
        if i >= 3:
            break
        print(row["idcaso"], row["ano"], row["estado"])
```

### 4.3 SPARQL (CPLT)

```bash
curl -sG 'https://datos.cplt.cl/sparql' \
  --data-urlencode 'query=SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5' \
  -H 'Accept: application/sparql-results+json'
```

Formatos de respuesta soportados:

| `Accept` | Formato |
|---|---|
| `application/sparql-results+json` | JSON (recomendado) |
| `application/sparql-results+xml` | XML |
| `text/csv` | CSV |

Grafos disponibles (verificados con `SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o } }`):

```
http://datos.cplt.cl/datos/infoprobidad/
http://datos.cplt.cl/ontologias/infoprobidad/
```

Los demas grafos (`virtrdf`, `ldp`, `owl`, `b3sonto`, `b3sifp`, `facets`, ...) son internos de
Virtuoso y **no contienen datos de negocio**. Filtrar siempre por `GRAPH`.

Consultas utiles:

```sparql
# Contar triples de InfoProbidad (verificado: 23.640.007)
SELECT (COUNT(*) AS ?n)
WHERE { GRAPH <http://datos.cplt.cl/datos/infoprobidad/> { ?s ?p ?o } }

# Tipos de entidad en InfoProbidad
SELECT DISTINCT ?tipo (COUNT(?s) AS ?n)
WHERE {
  GRAPH <http://datos.cplt.cl/datos/infoprobidad/> {
    ?s a ?tipo
  }
}
GROUP BY ?tipo
ORDER BY DESC(?n)
```

Rendimiento: las consultas con `COUNT(*)` sobre 23 M de triples tardan decenas de segundos.
Usar `LIMIT`, filtros `?s` concretos y cachear.

### 4.4 InfoLobby

**Catalogos CSV/Parquet** (verificados):

| Entidad | CSV | Parquet |
|---|---|---|
| Activos (lobbistas) | `activos.csv` | `activos.parquet` |
| Pasivos (sujetos pasivos) | `pasivos.csv` | `pasivos.parquet` |
| Audiencias | `audiencias.csv` | `audiencias.parquet` |
| Datos de audiencia | `datosAudiencia.csv` | `datosAudiencia.parquet` |
| Asistencias activos | `asistenciasActivos.csv` | `asistenciasActivos.parquet` |
| Asistencias pasivos | `asistenciasPasivos.csv` | `asistenciasPasivos.parquet` |
| Otros asistentes | `otrosAsistentes.csv` | `otrosAsistentes.parquet` |
| Donativos | `donativos.csv` | `donativos.parquet` |
| Representaciones | `representaciones.csv` | `representaciones.parquet` |
| Trabaja para | `trabajaPara.csv` | `trabajaPara.parquet` |

Patron: `https://datosinfolobby.cplt.cl/catalogos/<entidad>.csv` (tambien `.parquet`, `.rar`).

**Trampa de encoding:** no todos los CSV usan la misma codificacion.
`activos.csv` es UTF-8 con BOM; `audiencias.csv` es **UTF-16 LE con BOM**.
Detectar con los primeros bytes (`\xff\xfe` o `\xef\xbb\xbf`) antes de parsear.

```python
def read_csv_any(path):
    raw = open(path, "rb").read(4)
    enc = "utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8-sig"
    import csv
    with open(path, encoding=enc, newline="") as f:
        return list(csv.DictReader(f))
```

Esquema de `activos.csv` (verificado):

```
idActivo,uriActivo,nombreActivo,fichaActivoInfoLobby,uriTipo,uriPersona,
uriAudiencia,CodigoURIPersona,nombre,tipoActivo,uriOrganismo,
FechaInicio_Audiencia,organismo,IDORPortal,anio,trimestre,codigoActivo
```

**SPARQL de InfoLobby** (HTTP, no HTTPS):

```bash
curl -sG 'http://datos.infolobby.cl/sparql' \
  --data-urlencode 'query=SELECT ?s ?p ?o WHERE { GRAPH <http://datos.infolobby.cl/infolobby> { ?s ?p ?o } } LIMIT 10' \
  -H 'Accept: application/sparql-results+json'
```

Grafos de negocio: `http://datos.infolobby.cl/infolobby` y `http://datos.infolobby.cl/dw/infolobby`.
La ontologia usa prefijo `http://datos.infolobby.cl/ontologia/cplt#`.

**Nota de red:** `datos.infolobby.cl` no sirve HTTPS correctamente. Usar `http://`.

### 4.5 InfoProbidad

**Catalogos** (verificados; descargan el archivo completo, **ignoran `Range`**):

| Entidad | URL CSV |
|---|---|
| Declaraciones | `https://datos.cplt.cl/catalogos/infoprobidad/csvdeclaraciones` |
| Pasivos | `https://datos.cplt.cl/catalogos/infoprobidad/csvpasivo` |
| Actividades | `https://datos.cplt.cl/catalogos/infoprobidad/csvactividades` |
| Bien inmueble | `https://datos.cplt.cl/catalogos/infoprobidad/csvbienInmueble` |
| Bien mueble | `https://datos.cplt.cl/catalogos/infoprobidad/csvbienMueble` |
| Accion/derecho | `https://datos.cplt.cl/catalogos/infoprobidad/csvaccionDerecho` |
| Valor | `https://datos.cplt.cl/catalogos/infoprobidad/csvvalor` |

Variantes: `json<entidad>`, `xml<entidad>`, y sin prefijo (`.../declaraciones`).

Tamanos verificados: `csvdeclaraciones` = 48.477.760 bytes; `csvpasivo` = 39.881.177 bytes.

Esquema de `csvdeclaraciones` (verificado):

```
"UriDeclaracion","UriDeclarante","Tipo","Nombre","ApPaterno","ApMaterno",
"ComunaDesempenio","Comuna","Direccion","JefeServicio","EstadoCivil","Asuncion",
"Declaracion","Grado","PaisDesempenio","Institu...
```

Esquema de `csvpasivo` (verificado):

```
"UriDeclaracion","UriDeclarante","Nombre","ApPaterno","ApMaterno",
"TipoPasivo","Acreedor","MontoPasivo"
```

**Trampa:** `curl -r 0-300` **no** funciona; Virtuoso devuelve el archivo completo.
Usar `--max-time` amplio (>120 s) o descarga en background.

**SPARQL** (mismo endpoint que 4.3):

```sparql
SELECT ?s WHERE {
  GRAPH <http://datos.cplt.cl/datos/infoprobidad/> {
    ?s a <http://datos.cplt.cl/ontologias/infoprobidad/Persona>
  }
} LIMIT 10
```

### 4.6 Que SI se puede obtener

- Universo completo de casos del Consejo (2009 en adelante) con estado, tipo y organismo.
- Relacion caso -> estado, caso -> motivo.
- Organismos reclamados.
- Audiencias, lobbistas, sujetos pasivos, donativos y representaciones.
- Declaraciones de patrimonio e intereses, en CSV masivo o SPARQL.

### 4.7 Que NO se puede obtener

- **API REST de casos.** No existe; solo archivos estaticos.
- **`reclamantes.csv` / `.xml`.** Devuelven 404.
- **Datos en tiempo real.** Los archivos se regeneran por lotes.
- **Consulta SQL.** Solo SPARQL.
- **Descarga parcial de InfoProbidad.** El servidor ignora `Range`.
- **Raiz `https://datos.cplt.cl/`.** Devuelve 403; usar `/sparql` y `/catalogos/...` directamente.
- **`https://opendata.portaltransparencia.cl/`.** Devuelve 403 desde redes no residenciales;
  no usar como dependencia.

---

## 5. SINIM - presupuestos municipales (VERIFICADO)

No hay API documentada, pero el endpoint que usa el boton "Descargar planilla Excel" es estable
y devuelve datos completos. Tratarlo como **endpoint no documentado**: puede cambiar sin aviso.

### 5.1 Identidad

| Dato | Valor |
|---|---|
| App | `https://datos.sinim.gov.cl/` |
| Export | `https://datos.sinim.gov.cl/datos_municipales/obtener_datos_municipales.php` |
| Filtros | `https://datos.sinim.gov.cl/datos_municipales/obtener_datos_filtros.php` |
| Formato | SpreadsheetML (`application/x-msexcel`) |
| Auth | Ninguna |
| Costo | Gratis |

### 5.2 Descubrir IDs

**Subareas de un area:**

```bash
curl -s -X POST 'https://datos.sinim.gov.cl/datos_municipales/obtener_datos_filtros.php' \
  -d 'dato_area[]=1' \
  -H 'X-Requested-With: XMLHttpRequest'
```

**Variables de una subarea:**

```bash
curl -s -X POST 'https://datos.sinim.gov.cl/datos_municipales/obtener_datos_filtros.php' \
  -d 'dato_area[]=1' \
  -d 'dato_subarea[]=517' \
  -H 'X-Requested-With: XMLHttpRequest'
```

**Municipios de una region:**

```bash
curl -s -X POST 'https://datos.sinim.gov.cl/datos_municipales/obtener_datos_filtros.php' \
  -d 'region[]=120' \
  -H 'X-Requested-With: XMLHttpRequest'
```

Devuelve:

```json
[{"id":194,"municipio":"ANTOFAGASTA","id_legal":"02101"},
 {"id":195,"municipio":"MEJILLONES","id_legal":"02102"}]
```

**Regla:** `id` es el identificador interno que espera el export. `id_legal` es el codigo
de comuna (CUT simplificado) y **no** sirve para exportar.

### 5.3 Areas y subareas conocidas

| `dato_area[]` | Area |
|---|---|
| `1` | Administracion y finanzas municipales |
| `2` | Salud municipal |
| `3` | Educacion municipal |
| `4` | Desarrollo y gestion territorial |
| `5` | Social y comunitaria |
| `6` | Caracterizacion comunal |
| `7` | Genero |
| `570` | Cementerio |
| `608` | Recursos humanos municipal |
| `715` | (sin nombre) |

Subarea de presupuesto: **`517`** = `A.1. PRESUPUESTO INICIAL Y VIGENTE MUNICIPAL (M$)`.

Variables verificadas de la subarea 517:

| `id_dato` | Codigo | Nombre |
|---|---|---|
| `4211` | `BPIGM` | Presupuesto Inicial Gastos Municipales |
| `4212` | `BPVIM` | Presupuesto Vigente Sector Municipal |

Unidad: **miles de pesos (M$)**.

### 5.4 Exportar la planilla

```bash
curl -s -o presupuesto.xml \
  'https://datos.sinim.gov.cl/datos_municipales/obtener_datos_municipales.php?area[]=1&subarea[]=517&variables[]=4211&periodos[]=26&regiones[]=120&municipios[]=194&corrmon=0'
```

Parametros:

| Parametro | Formato | Ejemplo | Nota |
|---|---|---|---|
| `area[]` | int | `1` | Ver 5.3 |
| `subarea[]` | int | `517` | Ver 5.3 |
| `variables[]` | int o lista CSV | `4211,4212` | Varias variables separadas por coma |
| `periodos[]` | int o `T` | `26` / `T` | `26`=2025, `25`=2024, ... `T`=2001-2025 |
| `regiones[]` | int o `T` | `120` | Codigo de region |
| `municipios[]` | **id interno** o `T` | `194` / `T` | **No usar `02101`** |
| `corrmon` | `0` o `1` | `0` | `0` nominal; `1` corregido |

**Ejemplos que funcionan:**

```bash
# Un municipio, un año -> 5.017 bytes, 1 fila de datos
...&variables[]=4211&periodos[]=26&regiones[]=120&municipios[]=194&corrmon=0

# Todos los municipios de una region -> 6.395 bytes, 9 filas
...&variables[]=4211&periodos[]=26&regiones[]=120&municipios[]=T&corrmon=0

# Serie completa 2001-2025 para un municipio -> 12.994 bytes, 25 columnas
...&variables[]=4211&periodos[]=T&regiones[]=120&municipios[]=194&corrmon=0

# Dos variables -> columnas repetidas por variable
...&variables[]=4211,4212&periodos[]=26&regiones[]=120&municipios[]=194&corrmon=0

# Pais completo -> 63.360 bytes, 345 municipios
...&variables[]=4211&periodos[]=26&regiones[]=T&municipios[]=T&corrmon=0
```

**Si se usa `municipios[]=02101`, la respuesta es HTTP 200 pero sin filas de datos.**
Ese es el fallo silencioso mas comun.

### 5.5 Estructura de la respuesta

SpreadsheetML (XML de Excel). Filas:

```xml
<Row>
  <Cell><Data ss:Type="String">Valores en miles de pesos nominales (M$) de cada año.</Data></Cell>
</Row>
<Row>
  <Cell/><Cell/>
  <Cell><Data ss:Type="String">BPIGM (M$) Presupuesto Inicial Gastos Municipales</Data></Cell>
</Row>
<Row>
  <Cell><Data ss:Type="String">CODIGO</Data></Cell>
  <Cell><Data ss:Type="String">MUNICIPIO</Data></Cell>
  <Cell><Data ss:Type="String">2025</Data></Cell>
</Row>
<Row>
  <Cell><Data ss:Type="String">02101</Data></Cell>
  <Cell><Data ss:Type="String">ANTOFAGASTA</Data></Cell>
  <Cell><Data ss:Type="Number">183541651</Data></Cell>
</Row>
```

Parser:

```python
import xml.etree.ElementTree as ET
import requests

NS = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}

def sinim(area, subarea, variables, periodos, regiones, municipios, corrmon=0):
    params = {
        "area[]": area, "subarea[]": subarea,
        "variables[]": variables, "periodos[]": periodos,
        "regiones[]": regiones, "municipios[]": municipios,
        "corrmon": corrmon,
    }
    r = requests.get(
        "https://datos.sinim.gov.cl/datos_municipales/obtener_datos_municipales.php",
        params=params, timeout=90,
    )
    r.raise_for_status()
    root = ET.fromstring(r.content)
    rows = []
    for row in root.findall(".//ss:Row", NS):
        cells = []
        for cell in row.findall("ss:Cell", NS):
            data = cell.find("ss:Data", NS)
            cells.append(data.text if data is not None else None)
        rows.append(cells)
    return rows

rows = sinim(1, 517, "4211", "T", 120, 194)
print(rows[2])   # ['CODIGO', 'MUNICIPIO', '2025', ..., '2001']
print(rows[3][:4])  # ['02101', 'ANTOFAGASTA', '183541651', '156933868']
```

### 5.6 Vistas HTML complementarias (VERIFICADAS)

```bash
# Ficha comunal
curl -s 'https://datos.sinim.gov.cl/ficha_comunal.php?municipio=02101'

# Evolucion presupuestaria
curl -s 'https://datos.sinim.gov.cl/evolucion_presupuestaria.php'
```

Sirven para inspeccion humana; no son API.

### 5.7 Que SI se puede obtener

- Presupuesto inicial y vigente por municipio, en M$ nominales o corregidos.
- Serie historica **2001-2025** con `periodos[]=T`.
- Todos los municipios de una o varias regiones con `municipios[]=T`.
- Pais completo con `regiones[]=T` + `municipios[]=T` (verificado: 345 municipios).
- Multiples variables en una sola planilla.
- Cualquier area/subarea/variable del catalogo SINIM, no solo presupuesto.

### 5.8 Que NO se puede obtener

- **JSON.** Solo SpreadsheetML.
- **Documentacion oficial del endpoint.** No existe contrato; puede cambiar.
- **Series anteriores a 2001.**
- **Datos de municipios que no reportaron:** el valor es el string `"No Recepcionado"`,
  no `null`. Hay que normalizarlo.
- **Consultas ad hoc.** No hay filtros por texto ni agregaciones; se descarga y se calcula.
- **Codigos legales como parametro.** El export exige el `id` interno.

---

## 6. BCN / Ley Chile - REST con API-KEY (PARCIALMENTE VERIFICADO)

Funciona, pero **requiere credencial**. Sin key devuelve HTTP 401.

### 6.1 Identidad

| Dato | Valor |
|---|---|
| Base | `https://www.bcn.cl/leychile/api/v1` |
| Formato | JSON |
| Auth | API-KEY en query param `secret` |
| Licencia | CC BY-NC-ND 4.0 |
| Sin key | HTTP 401, cuerpo vacio (CloudFront) |

Esquema de seguridad declarado en el OpenAPI:

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: query
      name: secret
security:
  - ApiKeyAuth: [ ]
```

### 6.2 Uso

```bash
curl -s 'https://www.bcn.cl/leychile/api/v1/servicio/39/?secret=TU_API_KEY'
```

El catalogo se organiza como `/servicio/{id}/`, donde cada `id` es una consulta predefinida.
El listado completo de servicios esta en el OpenAPI:

```
https://www.bcn.cl/leychile/leychile-api-doc/assets/leychile-api-doc-v1.yaml
```

**Estado:** el sitio de documentacion devolvio 401 en la verificacion, por lo que **no se pudo
confirmar la semantica de cada `/servicio/{id}`**. La autenticacion y el rechazo sin key si
estan verificados. Obtener la key desde el formulario de contacto de BCN antes de integrar.

### 6.3 Que SI se puede obtener

- Texto y metadatos de leyes y normas (segun el servicio consultado).
- JSON estable, con contrato OpenAPI.

### 6.4 Que NO se puede obtener

- **Nada sin API-KEY.**
- **Uso comercial libre.** La licencia es CC BY-NC-ND 4.0: no comercial, sin derivadas.
- **Semantica de servicios no verificada en este entorno.** No asumir que `/servicio/39/`
  devuelve un tipo concreto sin probarlo con la key.

---

## 7. Lo que NO funciona (no perder tiempo)

| Fuente | Intento | Resultado real |
|---|---|---|
| **Senado** | `https://tramitacion.senado.cl/wspublico/tramitacion.php?boletin=8575` | Timeout / `"No existe el numero de boletin solicitado"` |
| **Senado** | `.../senadores_vigentes.php` | `"No existe informacion"` |
| **Senado** | `.../tramitacion.php?fecha=18/04/2023` | `"La fecha no puede exceder de un mes"` |
| **SERVEL** | API de resultados | No existe |
| **SERVEL** | `elecciones.servel.cl` ZIP/JSON en S3 | 403 en acceso directo |
| **SERVEL** | WordPress REST | Solo contenido del sitio, no resultados |
| **CPLT** | `reclamantes.csv` / `.xml` | 404 |
| **CPLT** | `https://opendata.portaltransparencia.cl/` | 403 |
| **CPLT** | `https://datos.cplt.cl/` (raiz) | 403 |
| **datos.gob.cl** | `datastore_search_sql` | `Action name not known` |
| **Camara** | `getPeriodoLegislativoActual` | `xsi:nil="true"` |
| **Camara** | `getSesionBoletinXML` | Respuesta vacia |
| **SINIM** | `sinim.subdere.gov.cl` | No resuelve DNS |

### 7.1 SERVEL: lo unico que si sirve

No hay API, pero las descargas funcionan:

```bash
# Candidaturas 2017 (XLSX, 364.900 bytes, HTTP 200)
curl -O 'https://www.servel.cl/wp-content/uploads/2022/12/Candidatos_2017_Electos_14-03-2018.xlsx'
```

Paginas oficiales utiles (HTTP 200 verificadas):

- `https://www.servel.cl/estadisticas-de-candidaturas/`
- `https://www.servel.cl/biblioteca-de-documentos/resultados-electorales-historicos/`
- `https://www.servel.cl/padrones-electorales-definitivos-y-nominas-de-inhabilitados-elecciones-2025/`

Los resultados historicos estan en dashboards **Power BI**: no son consumibles por API publica.
Planificar ETL sobre XLSX y validacion manual.

---

## 8. Claves de union entre fuentes

| Concepto | Fuente A | Fuente B | Clave | Nota |
|---|---|---|---|---|
| Diputado | Camara `DIPID` | Camara votos `DIPID` | `DIPID` | Entero estable |
| Proyecto | Camara `Boletin` (`8575-05`) | Senado (no disponible) | `boletin` sin sufijo | Camara acepta `8575` |
| Votacion | Camara `Votacion/ID` | Camara detalle | `prmVotacionID` | Entero |
| Sesion | Camara `Sesion/ID` | Camara detalle | `prmSesionID` | Entero |
| Municipio | SINIM `id` (interno) | SINIM `id_legal` | conversion via filtros | **No intercambiables** |
| Region | SINIM `regiones[]` | Codigo region | `120`, `131`, ... | Ver 5.3 |
| Caso CPLT | `casos.csv: idcaso` | `estadosPorCaso.csv: idcaso` | `idcaso` | Entero |
| Caso CPLT | `casos.csv: idcaso` | `motivosPorCaso.csv: idCaso` | ojo mayuscula | `idCaso` != `idcaso` |
| Organismo | `casos.csv: codigoOR` | `reclamados.csv: IDInstitucion,` | `codigoOR` vs UUID | **No coinciden**: uno es codigo, otro UUID |

---

## 9. Codigos y catalogos utiles (Camara)

| Campo | Codigo | Etiqueta |
|---|---|---|
| `Sexo` | `1` | Masculino |
| `Sexo` | `2` | Femenino |
| `Votacion/Resultado` | `1` | Aprobado |
| `Votacion/Resultado` | `2` | Rechazado |
| `Votacion/Tipo` | `6` | Unica |
| `Sesion/Tipo` | `60` | Ordinaria |
| `Sesion/Tipo` | `61` | Especial |
| `Sesion/Estado` | `1` | Celebrada |
| `Legislatura/Tipo` | `70` | Ordinaria |
| `Legislatura/Tipo` | `71` | Extraordinaria |
| `Comision/Tipo` | `2101` | Permanente |

No asumir que estos codigos son exhaustivos: la API devuelve otros valores. Guardar
`Codigo` + texto, no solo el texto.

---

## 10. Snippets de verificacion rapida (health checks)

```bash
# Camara
curl -s -o /dev/null -w 'camara %{http_code}\n' \
  'https://opendata.camara.cl/wscamaradiputados.asmx?WSDL'

# datos.gob.cl
curl -s 'https://datos.gob.cl/api/3/action/site_read'

# CPLT SPARQL
curl -s -o /dev/null -w 'cplt %{http_code}\n' \
  -G 'https://datos.cplt.cl/sparql' \
  --data-urlencode 'query=ASK { ?s ?p ?o }' \
  -H 'Accept: application/sparql-results+json'

# CPLT casos
curl -s -o /dev/null -w 'casos %{http_code} %{size_download}\n' \
  'https://consejotransparencia.cl/transparencia_activa/datoabierto/archivos/estadosPorCaso.csv'

# SINIM
curl -s -o /dev/null -w 'sinim %{http_code} %{content_type}\n' \
  'https://datos.sinim.gov.cl/datos_municipales/obtener_datos_municipales.php?area[]=1&subarea[]=517&variables[]=4211&periodos[]=26&regiones[]=120&municipios[]=194&corrmon=0'
```

Valores esperados: `camara 200`, `{"result": true, "success": true}`, `cplt 200`,
`casos 200` (`estadosPorCaso.csv` ~29 MB), `sinim 200 application/x-msexcel`.

---

## 11. Robustez, limites y licencias

### 11.1 Limites de tasa

Ninguna fuente publica cuotas. Recomendacion operativa:

- <= 1 request/segundo por host.
- Reintentos con backoff exponencial solo en `5xx` y timeouts.
- Cache en disco con `ETag` / `Last-Modified` cuando exista.
- `User-Agent` identificable con correo de contacto.

### 11.2 Timeouts observados

| Fuente | Timeout recomendado |
|---|---|
| Camara | 40 s |
| datos.gob.cl | 60 s |
| CPLT CSV | 120 s (`casos.csv` ~22 MB) |
| CPLT XML | 300 s (`estadosPorCaso.xml` ~224 MB) |
| CPLT SPARQL | 120 s (`COUNT` sobre 23 M triples) |
| InfoProbidad CSV | > 120 s, descargar en background |
| SINIM | 90 s (`periodos[]=T`) |

### 11.3 Licencias

| Fuente | Licencia |
|---|---|
| Camara | No publica terminos explicitos; uso civico/periodistico habitual |
| datos.gob.cl | Variable por dataset (`license_title`, `license_url`) |
| CPLT | No publica terminos explicitos en los archivos |
| InfoLobby / InfoProbidad | CC BY 4.0 (declarado en el portal) |
| SINIM | No publica terminos explicitos |
| BCN | CC BY-NC-ND 4.0 |

Verificar licencia por dataset antes de redistribuir. Para uso comercial, BCN queda excluido
por su licencia ND/NC.

### 11.4 Fragilidad

| Fuente | Estabilidad | Riesgo |
|---|---|---|
| Camara | Alta | Bajo; API oficial |
| datos.gob.cl | Alta | Bajo; CKAN estandar |
| CPLT SPARQL | Media | Virtuoso puede cambiar grafos |
| CPLT CSV | Media | Nombres y esquemas cambian sin aviso |
| InfoLobby catalogos | Media | Encoding inconsistente |
| SINIM | Media-baja | Endpoint no documentado |
| BCN | Alta con key | Requiere credencial |

---

## 12. Resumen ejecutivo en una tabla

| Fuente | API | Auth | Formato | Que da | Que no da |
|---|---|---|---|---|---|
| Camara | SOAP oficial | No | XML | Diputados, votos, sesiones, comisiones | Senado, asistencia, tramitacion |
| datos.gob.cl | CKAN REST | No | JSON | Catalogo + filas indexadas | SQL, contenido de PDF/XLSX |
| CPLT casos | Archivos | No | CSV/XML | Casos, estados, motivos | API REST, reclamantes |
| CPLT SPARQL | SPARQL 1.1 | No | JSON/CSV/XML | InfoProbidad (23,6 M triples) | Tiempo real, SQL |
| InfoLobby | Catalogos + SPARQL | No | CSV/Parquet/RDF | Audiencias, lobbistas, donativos | API REST |
| SINIM | Endpoint interno | No | SpreadsheetML | Presupuesto municipal 2001-2025 | JSON, contrato, <2001 |
| BCN | REST v1 | **API-KEY** | JSON | Leyes y normas | Sin key, uso comercial |

---

## 13. Checklist antes de codificar

- [ ] Lei la seccion 0 y respeto el SOAPAction `http://tempuri.org/...`.
- [ ] Para Camara, guardo `Codigo` y texto de cada atributo.
- [ ] Para datos.gob.cl, compruebo `datastore_active` **y** `total > 0`.
- [ ] Para CPLT, uso `utf-8-sig` y `delimiter=";"`.
- [ ] Para InfoLobby, detecto UTF-16 vs UTF-8 antes de parsear.
- [ ] Para InfoProbidad, no uso `Range` y doy timeout > 120 s.
- [ ] Para SINIM, uso el `id` interno, no `id_legal`.
- [ ] Para SINIM, normalizo `"No Recepcionado"` a nulo.
- [ ] Para BCN, tengo API-KEY y acepto CC BY-NC-ND.
- [ ] Cacheo y limito a 1 req/s.
- [ ] No dependo de Senado ni SERVEL como API.
