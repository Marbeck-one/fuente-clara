"""Guardrail: tres capas para que nadie use la IA de Fuente Clara para manipular.

1. Antes de la IA: largo máximo e intentos típicos de manipulación ("ignora tus instrucciones",
   "actúa como…"). Se rechazan sin llamar a la IA.
2. En la IA: el texto de la persona va entre marcas, y las reglas dicen que es dato, nunca instrucción.
3. Después de la IA: se revisa lo que escribió la IA antes de mostrarlo. Si opina, da un veredicto o
   filtra sus instrucciones, no se muestra. Los enlaces e imágenes se quitan siempre.

Las capas 1 y 3 son reglas fijas: no agregan costo ni espera.
"""
import re

from core.citas import normalizar

LARGO_MAXIMO = 1500  # el campo más largo (Verifica esto) admite 1.500 caracteres
MARCA_INICIO, MARCA_FIN = "<entrada_usuario>", "</entrada_usuario>"

# Capa 1. Se buscan sobre el texto normalizado (minúsculas y sin tildes).
# Apuntan a órdenes dirigidas a la IA ("tus reglas"), no a preguntas sobre reglas del colegio.
_MANIPULACION = [re.compile(p) for p in (
    r"\b(ignora|olvida|omite|salta|desobedece|desactiva|no sigas|no respetes|no cumplas)\w*\s+(\w+\s+){0,3}"
    r"tus\s+(instrucciones|reglas|indicaciones|restricciones|filtros|limites)",
    r"\b(ignora|olvida|omite|desobedece|no sigas)\w*\s+(\w+\s+){0,3}(instrucciones|reglas|indicaciones)\s+"
    r"(anteriores|previas|iniciales|originales|de arriba|del sistema)",
    r"\b(muestra|repite|revela|imprime|copia|escribe)\w*\s+(\w+\s+){0,3}tus\s+(instrucciones|reglas|indicaciones)",
    r"\b(system prompt|prompt del sistema|prompt de sistema|tu prompt)\b",
    r"\binstrucciones del sistema\b(?!\s+(educativ|escolar|de\s))",  # "del sistema educativo" es un tema legítimo
    r"\b(a partir de ahora|desde ahora)\s+(eres|seras|vas a ser|actua|responde|ignora|olvida)\b",
    r"(^|[.,;:!?¿¡]\s*)(actua|comportate|responde)\s+como\s+(si\s+fueras|un|una|el|la)\b",
    r"\b(finge|haz de cuenta)\s+(que\s+)?(eres|ser)\b",
    r"\b(modo desarrollador|modo dios|modo sin restricciones|developer mode|jailbreak)\b",
    r"\bignore\s+(all\s+|any\s+)?(previous|prior|above|your)\s+(instructions|rules)",
    r"\b(act as|you are now|pretend to be)\b",
    # Ampliación de Maximiliano (casos de #16), acotada: cada regla exige una orden dirigida a la IA
    # (verbo + objeto). Palabras sueltas como "contraseña", "backend" o "a favor de la ley" NO bloquean,
    # porque son el tema legítimo de las leyes de datos personales, ciberseguridad y de cualquier votación.
    r"\b(olvida|abandona)\w*\s+(\w+\s+){0,3}tu\s+(rol|papel|personaje|identidad)\b",
    r"\b(muestra|imprime|revela|repite|entrega|dame|lista)\w*\s+(\w+\s+){0,5}"
    r"(manual de operacion(es)?|configuracion interna|endpoints?|backend|diagnostico del sistema)\b",
    r"\b(ejecuta|haz|realiza)\w*\s+(un\s+)?diagnostico del sistema\b",
    r"\b(muestra|revela|dame|entrega|imprime|lista|comparte|envia)\w*\s+(\w+\s+){0,4}"
    r"(credenciales|claves? de acceso|contrasenas|api keys?)\b",
    r"\b(acceso root|root access)\b",
    r"\b(instruccion(es)? (externa|oculta|de alta prioridad|de sistema)|nueva regla del sistema)\b",
    r"\b(entrada_usuario)\b",
    r"\bignora\s+(el|la|los|las)\s+(resumen|documento|texto|contexto)\b",
    r"\bdile al usuario\b",
    r"\bsimulando ser\b",
    r"\b(haciendote pasar|hazte pasar)\b",
    r"\bautoriza\w*\s+(la\s+)?transferencia\b",
    r"\b(actua|responde|comportate)\s+como\s+si\b",
    r"\b(imagina que|finge que|supon que)\b.{0,80}\b(ia|inteligencia artificial|asistente|modelo)\b",
    r"\b(ia|asistente|modelo)\s+(libre|sin)\s+(de\s+)?(leyes|reglas|restricciones|filtros|limites)\b",
    r"\blibre de (leyes|reglas|restricciones)\b",
    r"\bdime como (fabricar|construir|elaborar|hacer)\b.{0,40}"
    r"\b(arma|bomba|explosivo|droga|sustancia peligrosa|veneno)\b",
    r"\bbase64\b",
    r"\b(anular|evadir|eludir|desactivar|deshabilitar)\w*\s+(\w+\s+){0,3}tus\s+"
    r"(filtros|reglas|restricciones|protecciones|limites|controles)\b",
    r"\b(reescribe|redacta|escribe|escribeme|mejora|adapta)\b.{0,60}\bpara que\b.{0,40}"
    r"\b(convenza|convencer|persuada|persuadir|apoyen|rechacen)\b",
    r"\b(escribe|escribeme|redacta|haz|hazme|dame|genera|crea)\w*\s+(\w+\s+){0,3}"
    r"(discurso|texto|mensaje|post|tweet|columna|volante|panfleto|argumento)\b.{0,30}\b(a favor|en contra)\b",
)]

# Capa 3. Lo que la IA nunca debe escribir con sus palabras (las citas del documento no se revisan).
_SALIDA_PROHIBIDA = [re.compile(p) for p in (
    r"\b(verdadero|verdadera|falso|falsa|fake|mentira|miente|bulo)\b",
    r"\b(te recomiendo|te recomendamos|recomendamos|deberias (votar|apoyar|rechazar|oponerte)|vota (por|a favor|en contra)"
    r"|en mi opinion|yo creo|creo que|considero que|me parece que|personalmente)\b",
    r"\bes (una )?(buena|mala|excelente|pesima|terrible) (ley|idea|medida|norma|propuesta)\b",
    r"(reglas obligatorias|entrada_usuario|responde unicamente con un objeto json|eres fuente clara)",
)]


def es_manipulacion(texto):
    """Capa 1: True si el texto es demasiado largo o trae un intento típico de manipulación."""
    texto = str(texto)
    return len(texto) > LARGO_MAXIMO or any(p.search(normalizar(texto)) for p in _MANIPULACION)


def delimitar(texto):
    """Capa 2: el texto de la persona entre marcas. Se borran las marcas que la persona haya escrito."""
    limpio = re.sub(r"<\s*/?\s*entrada_usuario\s*>", "", str(texto), flags=re.IGNORECASE)
    return f"{MARCA_INICIO}\n{limpio}\n{MARCA_FIN}"


def _sin_enlaces(texto):
    texto = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", str(texto))   # imágenes
    texto = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texto)      # enlaces: queda solo su texto
    texto = re.sub(r"<[^>]+>", "", texto)                       # etiquetas HTML
    return re.sub(r"(https?://|www\.)\S+", "[enlace quitado]", texto)


def salida_segura(r):
    """Capa 3: quita enlaces de todo lo que escribió la IA y devuelve False si opinó, dio un veredicto
    o filtró sus instrucciones. No revisa la afirmación de Verifica (repite lo que pegó la persona)."""
    revisar = []
    for campo in ("respuesta", "que_cambia", "organismo", "justificacion", "borrador"):
        if campo in r:
            r[campo] = _sin_enlaces(r[campo])
            revisar.append(r[campo])
    for c in r.get("comparaciones") or []:
        c["afirmacion"], c["texto_oficial"] = _sin_enlaces(c["afirmacion"]), _sin_enlaces(c["texto_oficial"])
        revisar.append(c["texto_oficial"])
    return not any(p.search(normalizar(t)) for t in revisar for p in _SALIDA_PROHIBIDA)
