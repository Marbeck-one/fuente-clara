"""Carga un documento oficial (PDF o TXT) y lo segmenta por artículo, conservando la página."""
import re
from collections import Counter
from pathlib import Path

import yaml
from pypdf import PdfReader

from core.citas import normalizar

CARPETA = Path(__file__).resolve().parents[1] / "data" / "documentos"
# "Artículo 1.-", "Artículo 2°.-", "ARTÍCULO ÚNICO.", "Artículo primero transitorio.-", '"Artículo 10 bis.-'
# Exige puntuación después del número para no confundir con referencias ("el artículo 5 de la ley...").
RE_ARTICULO = re.compile(
    r"(?im)^[ \t]*[\"“«]?[ \t]*(art[íi]culo\s+(?:\d+|[a-záéíóúñ]+)"
    r"(?:\s+(?:bis|ter|qu[áa]ter|quinquies|sexies|transitorio))?)\s*[°º]?\s*(?:\.-|\.|:|-|–)")
# Numerales de una ley que modifica otra: "4. Reemplázase…", "2. En el artículo 10:".
RE_NUMERAL = re.compile(
    r"(?m)^[ \t]*(\d+)\.[ \t]+(?:Agr[ée]g|Reempl[áa]z|Sustit[úu]y|Incorp[óo]r|Introd[úu]c|Interc[áa]l|"
    r"Elim[íi]n|Supr[íi]m|Modif[íi]c|Der[óo]g|En (?:el|la|los|las) )")
# En los TXT, una línea "--- Página N ---" o un salto de página (\f) marca el inicio de una página nueva.
RE_PAGINA_TXT = re.compile(r"(?im)^-{3,}\s*p[áa]gina\s*\d*\s*-{3,}[ \t]*$|\f")


def listar():
    """Documentos registrados en catalogo.yaml (con su fuente oficial) cuyo archivo existe."""
    catalogo = yaml.safe_load((CARPETA / "catalogo.yaml").read_text(encoding="utf-8")) or {}
    return [d for d in catalogo.get("documentos") or [] if (CARPETA / d["archivo"]).exists()]


def _sin_repetidas(paginas):
    """Quita encabezados y pies que se repiten en casi todas las páginas (ej. "página 2 de 4")."""
    if len(paginas) < 3:
        return paginas
    clave = lambda linea: re.sub(r"\d+", "#", linea.strip())  # noqa: E731
    veces = Counter(k for p in paginas for k in {clave(linea) for linea in p.splitlines()} if k)
    repetidas = {k for k, n in veces.items() if n >= 0.6 * len(paginas)}
    return ["\n".join(linea for linea in p.splitlines() if clave(linea) not in repetidas) for p in paginas]


def _paginas(ruta):
    if ruta.suffix.lower() == ".pdf":
        textos = [p.extract_text() or "" for p in PdfReader(ruta).pages]
        return _sin_repetidas([re.sub(r"(\w)-\n(\w)", r"\1\2", t) for t in textos])  # une palabras cortadas
    return RE_PAGINA_TXT.split(ruta.read_text(encoding="utf-8"))


def _etiqueta(texto):
    return " ".join(["Artículo"] + [p.lower() for p in texto.split()[1:]])


def _fragmentos(paginas):
    """Corta por artículo y, en leyes modificatorias, por numeral. Un trozo que cruza de página se divide."""
    fragmentos, etiqueta, articulo, base = [], "Encabezado", "Encabezado", None
    for numero, texto in enumerate(paginas, start=1):
        marcas = sorted([(m.start(), "", _etiqueta(m.group(1))) for m in RE_ARTICULO.finditer(texto)]
                        + [(m.start(), m.group(1), "") for m in RE_NUMERAL.finditer(texto)])
        cortes = [(0, etiqueta)]
        for inicio, numeral, nombre in marcas:
            if nombre:
                articulo = etiqueta = nombre
            else:  # el numeral 1 fija el artículo que contiene la lista de modificaciones
                base = articulo if numeral == "1" or base is None else base
                etiqueta = f"{base}, numeral {numeral}"
            cortes.append((inicio, etiqueta))
        for i, (inicio, etq) in enumerate(cortes):
            fin = cortes[i + 1][0] if i + 1 < len(cortes) else len(texto)
            trozo = texto[inicio:fin].strip()
            if trozo:
                fragmentos.append({"articulo": etq, "pagina": numero, "texto": trozo, "norm": normalizar(trozo)})
    return fragmentos


def cargar(archivo):
    """Devuelve los metadatos del catálogo más los fragmentos del documento."""
    meta = next(d for d in listar() if d["archivo"] == archivo)
    fragmentos = _fragmentos(_paginas(CARPETA / archivo))
    return {**meta, "fragmentos": fragmentos, "texto_norm": " ".join(f["norm"] for f in fragmentos)}


def para_prompt(doc):
    """Documento completo para el contexto del modelo, con etiquetas de artículo y página."""
    partes = [f"TÍTULO: {doc['titulo']}", "=== INICIO DEL DOCUMENTO ==="]
    partes += [f"[{f['articulo']} | página {f['pagina']}]\n{f['texto']}" for f in doc["fragmentos"]]
    return "\n\n".join(partes + ["=== FIN DEL DOCUMENTO ==="])
