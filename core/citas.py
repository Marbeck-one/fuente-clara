"""Verificación de citas: comprueba que cada texto citado exista literalmente en el documento."""
import re
import unicodedata

# La regla de los prompts: la cita debe ser un fragmento continuo de 8 a 40 palabras.
# El mínimo evita "citas" triviales como "de la ley"; el máximo evita párrafos enteros.
PALABRAS_MINIMAS = 8
PALABRAS_MAXIMAS = 40
# Las comillas se eliminan: al escribir JSON, los modelos suelen cambiar comillas dobles por simples.
_EQUIVALENCIAS = str.maketrans({'"': None, "'": None, "“": None, "”": None, "«": None, "»": None, "‘": None,
                                "’": None, "–": "-", "—": "-", "º": "°", " ": " "})


def normalizar(texto):
    """Minúsculas, sin tildes ni comillas, guiones unificados y espacios colapsados."""
    texto = unicodedata.normalize("NFKD", str(texto).translate(_EQUIVALENCIAS).lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip()


def verificar(citas, doc):
    """Marca cada cita como verificada o no. Si existe, usa el artículo y página reales del documento.

    La cita debe estar contenida en UN solo fragmento (artículo/página). Buscarla en el texto
    concatenado permitiría que una cita que cruza dos artículos quedara "verificada" con la
    página y el artículo que inventó el modelo.
    """
    resultado = []
    for cita in citas if isinstance(citas, list) else []:
        if not isinstance(cita, dict):
            continue
        literal = " ".join(str(cita.get("texto_literal", "")).split())
        buscado = normalizar(literal).strip(" .,;:\"'")
        palabras = len(buscado.split())
        fragmento = None
        if PALABRAS_MINIMAS <= palabras <= PALABRAS_MAXIMAS:
            fragmento = next((f for f in doc["fragmentos"] if buscado in f["norm"]), None)
        ok = fragmento is not None

        articulo, pagina = str(cita.get("articulo", "?")), cita.get("pagina", "?")
        if articulo.isdigit():
            articulo = f"Artículo {articulo}"
        if ok:
            articulo, pagina = fragmento["articulo"], fragmento["pagina"]
        resultado.append({"articulo": articulo, "pagina": pagina, "texto_literal": literal, "verificada": ok})
    return resultado


def hay_verificada(citas):
    return any(c["verificada"] for c in citas)
