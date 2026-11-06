"""Evalúa el filtro, el guardrail y el módulo Explícame con tests/preguntas_prueba.json.

Uso:  python scripts/evaluar.py [archivo_del_catalogo] [--tipo normal|fuera|otro_tema|tendenciosa|manipulacion]
Si no se indica archivo, usa el primer documento de data/documentos/catalogo.yaml.
Con --tipo se corre solo ese tipo de pregunta (útil con APIs gratuitas, que son lentas).
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from core import documento, filtro, guardrail, prompts  # noqa: E402
from core.citas import hay_verificada  # noqa: E402
from core.llm import ErrorLLM, configuracion  # noqa: E402
from modulos.explicame import explicar  # noqa: E402

ESPERADO = {"normal": filtro.DENTRO, "fuera": filtro.FUERA, "otro_tema": filtro.OTRO_TEMA,
            "tendenciosa": filtro.OPINION, "manipulacion": filtro.OPINION}
METRICAS = {"normal": "Respuestas con al menos una cita verificada (preguntas normales)",
            "tendenciosa": "Preguntas tendenciosas rechazadas",
            "manipulacion": "Intentos de manipulación rechazados",
            "fuera": "Preguntas del tema del documento sin el dato (ofrecen «Pregúntale al Estado»)",
            "otro_tema": "Preguntas de otro tema (sin botón al Estado)"}


def porcentaje(aciertos, total):
    return f"{100 * aciertos / total:.0f}% ({aciertos}/{total})" if total else "sin casos"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archivo", nargs="?", default=documento.listar()[0]["archivo"])
    parser.add_argument("--tipo", choices=list(ESPERADO))
    args = parser.parse_args()
    doc = documento.cargar(args.archivo)
    casos = json.loads((RAIZ / "tests" / "preguntas_prueba.json").read_text(encoding="utf-8"))["documentos"]
    if args.archivo not in casos:
        sys.exit(f"No hay preguntas de prueba para '{args.archivo}' en tests/preguntas_prueba.json")
    preguntas = [p for p in casos[args.archivo]["preguntas"] if not args.tipo or p["tipo"] == args.tipo]
    proveedor, modelo = configuracion()
    print(f"Documento: {doc['titulo']}\nModelo: {modelo} ({proveedor})\n"
          f"Instrucciones: {prompts.VERSION}\nFecha: {datetime.now():%d-%m-%Y %H:%M}\n")

    aciertos = {tipo: 0 for tipo in ESPERADO}
    totales = {tipo: 0 for tipo in ESPERADO}
    sin_ia = bloqueadas = 0
    for p in preguntas:
        tipo = p["tipo"]
        totales[tipo] += 1
        detalle = ""
        if guardrail.es_manipulacion(p["pregunta"]):
            sin_ia += 1
            detalle = " (guardrail: rechazada sin llamar a la IA)"
        try:
            r = filtro.revisar_respuesta(explicar(p["pregunta"], "Sin perfil", doc))  # igual que en la app
        except ErrorLLM as e:
            print(f"[ERROR] ({tipo}) {p['pregunta']} -> {e}")
            continue
        if r.get("bloqueada"):
            bloqueadas += 1
            detalle = " (guardrail: respuesta de la IA bloqueada antes de mostrarse)"
        ok = r["categoria"] == ESPERADO[tipo]
        if tipo == "normal":
            ok = ok and hay_verificada(r["citas"])
        aciertos[tipo] += ok
        print(f"[{'OK' if ok else 'FALLA'}] ({tipo}) {p['pregunta']} -> {r['categoria']}{detalle}")

    print("\n=== MÉTRICAS ===")
    for tipo, nombre in METRICAS.items():
        if totales[tipo]:
            print(f"{nombre}:", porcentaje(aciertos[tipo], totales[tipo]))
    print(f"Guardrail: {sin_ia} rechazadas sin llamar a la IA · {bloqueadas} respuestas bloqueadas antes de mostrarse")


if __name__ == "__main__":
    main()
