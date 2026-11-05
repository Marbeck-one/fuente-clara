"""Filtro de alcance: clasifica la entrada antes de llamar a cualquier módulo."""
from core import prompts
from core.documento import para_prompt
from core.llm import complete

DENTRO = "dentro_del_documento"
FUERA = "fuera_del_documento"
OPINION = "opinion_o_politica_partidista"

MENSAJE_FIJO = (
    "Fuente Clara solo explica lo que dice el documento cargado. No entrega opiniones, no evalúa si algo "
    "es bueno o malo, no recomienda cómo votar y no responde sobre candidaturas, partidos o personas en "
    "cargos públicos. Puedes preguntar qué dice el texto sobre un tema concreto."
)


def clasificar(texto, doc, tipo="pregunta"):
    """Devuelve DENTRO, FUERA u OPINION. Si el modelo responde algo inesperado, se toma la opción prudente."""
    datos = complete(prompts.FILTRO, f"{para_prompt(doc)}\n\nTIPO DE ENTRADA: {tipo}\nENTRADA DEL USUARIO:\n{texto}")
    categoria = str(datos.get("categoria", "")).strip()
    return categoria if categoria in (DENTRO, FUERA, OPINION) else OPINION
