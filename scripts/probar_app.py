"""Prueba de integración real de los tres módulos. Consume la API configurada en .env.

Uso:  python scripts/probar_app.py
No imprime ni guarda la clave. Sirve para comprobar que el modelo responde y que las
categorías, citas y borrador funcionan antes de la demo.
"""
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from core import documento, filtro  # noqa: E402
from core.citas import hay_verificada  # noqa: E402
from core.llm import ErrorLLM  # noqa: E402
from modulos.explicame import explicar  # noqa: E402
from modulos.transparencia import preparar_solicitud  # noqa: E402
from modulos.verifica import comparar  # noqa: E402


def _caso(nombre, funcion, comprobar, fallos):
    """Ejecuta un módulo como lo hace la app y valida el resultado sin mostrar la clave."""
    inicio = time.time()
    try:
        r = filtro.revisar_respuesta(funcion())
    except ErrorLLM as e:
        print(f"[FALLA] {nombre}: {e}")
        fallos.append(nombre)
        return None
    ok, detalle = comprobar(r)
    print(f"[{'OK' if ok else 'FALLA'}] {nombre} ({time.time() - inicio:.1f}s) · {detalle}")
    if not ok:
        fallos.append(nombre)
    return r


def main():
    catalogo = documento.listar()
    if not catalogo:
        sys.exit("No hay documentos en el catálogo.")
    doc = documento.cargar(catalogo[0]["archivo"])
    print(f"Documento: {doc['titulo']}\n")

    fallos = []

    _caso(
        "Explícame · pregunta normal",
        lambda: explicar("¿Puedo usar el celular en el recreo si estoy en la media?", "Estudiante", doc),
        lambda r: (r.get("categoria") == filtro.DENTRO and hay_verificada(r.get("citas") or []),
                   f"categoría={r.get('categoria')}, citas verificadas="
                   f"{sum(c['verificada'] for c in r.get('citas') or [])}"),
        fallos,
    )

    _caso(
        "Explícame · opinión",
        lambda: explicar("¿Es buena idea prohibir los celulares? Dame tu opinión.", "Estudiante", doc),
        lambda r: (r.get("categoria") == filtro.OPINION, f"categoría={r.get('categoria')}"),
        fallos,
    )

    _caso(
        "Explícame · otro tema",
        lambda: explicar("¿Cuánto mide el monte Everest?", "Estudiante", doc),
        lambda r: (r.get("categoria") == filtro.OTRO_TEMA, f"categoría={r.get('categoria')}"),
        fallos,
    )

    def comprobar_verifica(r):
        comparaciones = r.get("comparaciones") or []
        respaldada = [c for c in comparaciones if c.get("etiqueta") == "dice_otra_cosa"]
        ok = bool(respaldada) and any(hay_verificada(c.get("citas") or []) for c in respaldada)
        etiquetas = [c.get("etiqueta") for c in comparaciones]
        return ok, f"categoría={r.get('categoria')}, etiquetas={etiquetas}"

    _caso(
        "Verifica esto · afirmación falsa",
        lambda: comparar("Desde marzo los profes sí pueden usar el celular en clases, pero los alumnos no.", doc),
        comprobar_verifica,
        fallos,
    )

    def comprobar_transparencia(r):
        borrador = r.get("borrador") or ""
        ok = (r.get("categoria") == filtro.FUERA and bool(r.get("organismo"))
              and "solicito la siguiente información" in borrador and "[TU NOMBRE]" in borrador)
        return ok, f"categoría={r.get('categoria')}, organismo={r.get('organismo')}"

    _caso(
        "Pregúntale al Estado · dato que falta",
        lambda: preparar_solicitud("¿Cuántos colegios actualizaron su reglamento interno antes del 30 de junio?", doc),
        comprobar_transparencia,
        fallos,
    )

    print(f"\n{'Prueba de integración OK' if not fallos else f'{len(fallos)} caso(s) fallaron'}")
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
