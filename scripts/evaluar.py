"""Evalúa el filtro y el módulo Explícame con tests/preguntas_prueba.json.

Uso:  python scripts/evaluar.py [archivo_del_catalogo]
Si no se indica archivo, usa el primer documento de data/documentos/catalogo.yaml.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from core import documento, filtro  # noqa: E402
from core.citas import hay_verificada  # noqa: E402
from core.llm import ErrorLLM, configuracion  # noqa: E402
from modulos.explicame import explicar  # noqa: E402

ESPERADO = {"normal": filtro.DENTRO, "fuera": filtro.FUERA, "tendenciosa": filtro.OPINION}


def porcentaje(aciertos, total):
    return f"{100 * aciertos / total:.0f}% ({aciertos}/{total})" if total else "sin casos"


def main():
    archivo = sys.argv[1] if len(sys.argv) > 1 else documento.listar()[0]["archivo"]
    doc = documento.cargar(archivo)
    casos = json.loads((RAIZ / "tests" / "preguntas_prueba.json").read_text(encoding="utf-8"))["documentos"]
    if archivo not in casos:
        sys.exit(f"No hay preguntas de prueba para '{archivo}' en tests/preguntas_prueba.json")
    preguntas = casos[archivo]["preguntas"]
    proveedor, modelo = configuracion()
    print(f"Documento: {doc['titulo']}\nModelo: {modelo} ({proveedor})\n")

    aciertos = {tipo: 0 for tipo in ESPERADO}
    totales = {tipo: 0 for tipo in ESPERADO}
    for p in preguntas:
        tipo = p["tipo"]
        totales[tipo] += 1
        try:
            r = explicar(p["pregunta"], "Sin perfil", doc)
        except ErrorLLM as e:
            print(f"[ERROR] ({tipo}) {p['pregunta']} -> {e}")
            continue
        ok = r["categoria"] == ESPERADO[tipo]
        if tipo == "normal":
            ok = ok and hay_verificada(r["citas"])
        aciertos[tipo] += ok
        print(f"[{'OK' if ok else 'FALLA'}] ({tipo}) {p['pregunta']} -> {r['categoria']}")

    print("\n=== MÉTRICAS ===")
    print("Respuestas con al menos una cita verificada (preguntas normales):",
          porcentaje(aciertos["normal"], totales["normal"]))
    print("Preguntas tendenciosas rechazadas:", porcentaje(aciertos["tendenciosa"], totales["tendenciosa"]))
    print("Preguntas fuera del documento detectadas:", porcentaje(aciertos["fuera"], totales["fuera"]))


if __name__ == "__main__":
    main()
