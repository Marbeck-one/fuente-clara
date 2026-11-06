"""Filtro de alcance: clasifica la entrada antes de llamar a cualquier módulo. Aplica el guardrail (core/guardrail.py)."""
from core import guardrail, prompts
from core.documento import para_prompt
from core.llm import complete

DENTRO = "dentro_del_documento"
FUERA = "fuera_del_documento"  # mismo tema del documento, pero falta el dato
OTRO_TEMA = "otro_tema"  # el documento no trata ese asunto
OPINION = "opinion_o_politica_partidista"

MENSAJE_FIJO = (
    "Fuente Clara solo explica lo que dice el documento cargado. No entrega opiniones, no evalúa si algo "
    "es bueno o malo, no recomienda cómo votar y no responde sobre candidaturas, un partido en particular "
    "o personas en cargos públicos. Puedes preguntar qué dice el texto sobre un tema concreto."
)


def clasificar(texto, doc, tipo="pregunta"):
    """Devuelve DENTRO, FUERA, OTRO_TEMA u OPINION. Si el modelo responde algo inesperado, se toma la opción prudente."""
    if guardrail.es_manipulacion(texto):  # capa 1: se rechaza sin llamar a la IA
        return OPINION
    datos = complete(prompts.FILTRO, f"{para_prompt(doc)}\n\nTIPO DE ENTRADA: {tipo}\n{guardrail.delimitar(texto)}")
    categoria = str(datos.get("categoria", "")).strip()
    return categoria if categoria in (DENTRO, FUERA, OTRO_TEMA, OPINION) else OPINION


def revisar_respuesta(r):
    """Capa 3 del guardrail: si la IA opinó, dio un veredicto o filtró sus instrucciones, no se muestra."""
    if r.get("categoria") == OPINION or guardrail.salida_segura(r):
        return r
    return {"categoria": OPINION, "bloqueada": "salida"}
