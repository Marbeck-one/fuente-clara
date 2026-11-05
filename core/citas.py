"""Verificación de citas: comprueba que cada texto citado exista literalmente en el documento."""
import re
import unicodedata

LARGO_MINIMO = 15  # evita "citas" triviales como "de la ley"
_EQUIVALENCIAS = str.maketrans({"“": '"', "”": '"', "«": '"', "»": '"', "‘": "'", "’": "'",
                                "–": "-", "—": "-", "º": "°", " ": " "})


def normalizar(texto):
    """Minúsculas, sin tildes, comillas y guiones unificados y espacios colapsados."""
    texto = unicodedata.normalize("NFKD", str(texto).translate(_EQUIVALENCIAS).lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip()


def verificar(citas, doc):
    """Marca cada cita como verificada o no. Si existe, usa el artículo y página reales del documento."""
    resultado = []
    for cita in citas if isinstance(citas, list) else []:
        if not isinstance(cita, dict):
            continue
        literal = " ".join(str(cita.get("texto_literal", "")).split())
        buscado = normalizar(literal).strip(" .,;:\"'")
        ok = len(buscado) >= LARGO_MINIMO and buscado in doc["texto_norm"]
        articulo, pagina = str(cita.get("articulo", "?")), cita.get("pagina", "?")
        if articulo.isdigit():
            articulo = f"Artículo {articulo}"
        if ok:
            fragmento = next((f for f in doc["fragmentos"] if buscado in f["norm"]), None)
            if fragmento:
                articulo, pagina = fragmento["articulo"], fragmento["pagina"]
        resultado.append({"articulo": articulo, "pagina": pagina, "texto_literal": literal, "verificada": ok})
    return resultado


def hay_verificada(citas):
    return any(c["verificada"] for c in citas)
