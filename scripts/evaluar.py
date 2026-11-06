"""Evalúa el filtro, el guardrail, Explícame y Verifica esto con tests/preguntas_prueba.json.

Uso:
    python scripts/evaluar.py [archivo_del_catalogo] [--tipo normal|fuera|otro_tema|tendenciosa|manipulacion]
    python scripts/evaluar.py [archivo_del_catalogo] --verifica

Si no se indica archivo, usa el primer documento de data/documentos/catalogo.yaml.
Con --tipo se corre solo ese tipo de pregunta.
Con --verifica se evalúan solo las afirmaciones de "Verifica esto" (gasta más API).
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


def evaluar_verifica(doc, caso):
    """Corre las afirmaciones de Verifica esto y mide etiqueta correcta y cita verificada."""
    from modulos import verifica  # importa Streamlit solo cuando se usa este modo

    afirmaciones = caso.get("afirmaciones_para_verifica") or []
    if not afirmaciones:
        sys.exit("No hay 'afirmaciones_para_verifica' para este documento en tests/preguntas_prueba.json")

    aciertos = con_cita = requieren_cita = 0
    for a in afirmaciones:
        try:
            r = filtro.revisar_respuesta(verifica.comparar(a["texto"], doc))
        except ErrorLLM as e:
            print(f"[ERROR] {a['texto']} -> {e}")
            continue
        comparaciones = r.get("comparaciones") or []
        etiquetas = [c.get("etiqueta") for c in comparaciones]
        ok = a["esperado"] in etiquetas
        aciertos += ok

        if a["esperado"] in ("respalda", "dice_otra_cosa"):
            requieren_cita += 1
            tiene_cita = any(c.get("etiqueta") == a["esperado"] and hay_verificada(c.get("citas") or [])
                             for c in comparaciones)
            con_cita += tiene_cita
        detalle = "" if ok else f" -> obtuve {etiquetas or 'sin comparaciones'}"
        print(f"[{'OK' if ok else 'FALLA'}] (verifica) {a['texto']}{detalle}")

    print("\n=== MÉTRICAS DE VERIFICA ===")
    print("Etiqueta correcta:", porcentaje(aciertos, len(afirmaciones)))
    print("Con cita verificada (cuando corresponde):", porcentaje(con_cita, requieren_cita))
    return 0 if aciertos == len(afirmaciones) else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archivo", nargs="?", default=documento.listar()[0]["archivo"])
    parser.add_argument("--tipo", choices=list(ESPERADO))
    parser.add_argument("--verifica", action="store_true", help="evalúa solo las afirmaciones de Verifica esto")
    args = parser.parse_args()
    doc = documento.cargar(args.archivo)
    casos = json.loads((RAIZ / "tests" / "preguntas_prueba.json").read_text(encoding="utf-8"))["documentos"]
    if args.archivo not in casos:
        sys.exit(f"No hay preguntas de prueba para '{args.archivo}' en tests/preguntas_prueba.json")
    if args.verifica:
        return evaluar_verifica(doc, casos[args.archivo])
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
    sys.exit(main())
