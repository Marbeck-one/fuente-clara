"""IA simulada: sin red, sin claves y sin gastar tokens. Solo para pruebas.

Se importa antes de arrancar Streamlit (ver scripts/probar_voz.py), así la app usa estas respuestas en vez de llamar a un modelo. Las respuestas citan textos reales de la Ley 21.801, así que la verificación
de citas funciona igual que en la app de verdad.
"""
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import prompts  # noqa: E402

CITA_1 = ('Prohíbese el uso de dispositivos móviles electrónicos de comunicación personal, en adelante '
          '"dispositivos móviles", en los establecimientos educacionales que imparten niveles de educación '
          'parvularia, básica o media.')
CITA_2 = "Lo dispuesto en el artículo 10 bis entrará en vigencia al inicio del año escolar 2026."


def _pregunta(user):
    """Lo que escribió la persona, para que cada consulta tenga una respuesta distinta."""
    return user.split("<entrada_usuario>")[-1].split("</entrada_usuario>")[0].strip()[:40]


def falsa(system, user, imagen=None):
    if system == prompts.FILTRO:
        return {"categoria": "dentro_del_documento"}
    if system == prompts.EXPLICAME:
        cita = [{"articulo": "Artículo 10 bis", "pagina": 1, "texto_literal": CITA_1}]
        return {"en_documento": "true",
                "frases": [{"texto": f"La ley [prohíbe](https://ejemplo.cl) el uso de celulares sobre «{_pregunta(user)}».",
                            "citas": cita}],
                "que_cambia_para_ti": [{"texto": "Tu colegio debe actualizar su reglamento interno.", "citas": cita}]}
    if system == prompts.VERIFICA:
        return {"comparaciones": [{"afirmacion": _pregunta(user), "etiqueta": "respalda",
                                   "texto_oficial": "La ley prohíbe los dispositivos móviles en los colegios.",
                                   "citas": [{"articulo": "Artículo 10 bis", "pagina": 1, "texto_literal": CITA_1}]}]}
    if system == prompts.TRANSPARENCIA:
        return {"organismo": "Ministerio de Educación", "respuesta": f"Solicito información sobre {_pregunta(user)}.",
                "justificacion": "El Ministerio de Educación tiene a su cargo la política escolar.",
                "citas": [{"articulo": "Artículo 10 bis", "pagina": 1, "texto_literal": CITA_2}]}
    return {}



def instalar():
    """Hace que la app use `falsa` en vez de llamar a un modelo. Solo para el lanzador de pruebas en navegador."""
    import core.llm as llm
    os.environ.setdefault("LLM_PROVIDER", "openai")
    os.environ.setdefault("OPENAI_API_KEY", "simulada")
    os.environ.setdefault("VOTOS_ARCHIVO", str(Path(tempfile.gettempdir()) / "votos_simulados.jsonl"))
    os.environ.setdefault("LIMITE_CONSULTAS_SESION", "200")
    os.environ.setdefault("LIMITE_CONSULTAS_MINUTO", "200")
    llm.complete = falsa
