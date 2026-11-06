"""Mide cada módulo de Fuente Clara con tests/preguntas_prueba.json y arma la tabla de resultados.

Uso:  python scripts/evaluar.py [archivo_del_catalogo] [--modulo explicame|verifica|estado] [--tipo TIPO]
Si no se indica archivo, usa el primer documento de data/documentos/catalogo.yaml.
--modulo corre un solo módulo. --tipo corre un solo tipo de pregunta de Explícame
(normal, fuera, otro_tema, tendenciosa o manipulacion). Sirven con APIs gratuitas, que son lentas.

Qué mide:
- Explícame: todas las preguntas de prueba, con el filtro y el guardrail igual que en la app.
- Verifica esto: las 'afirmaciones_para_verifica'. Acierta si la app muestra como válida una
  comparación con la etiqueta esperada.
- Pregúntale al Estado: las preguntas 'fuera' (el documento no tiene el dato). Lista el organismo
  sugerido para que una persona marque si es razonable.
- Tiempo promedio por consulta que llega a la IA, sin contar la espera obligada de LLM_INTERVALO_MIN.
- Votos 👍/👎 que dejaron las personas en la app con este documento y este modelo (data/votos).
Al final imprime una tabla en Markdown, lista para el pitch y para DECLARACION_IA.md.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from core import documento, filtro, guardrail, prompts, votos  # noqa: E402
from core.citas import hay_verificada  # noqa: E402
from core.llm import ErrorLLM, configuracion, segundos_esperados  # noqa: E402
from modulos.explicame import explicar  # noqa: E402
from modulos.transparencia import preparar_solicitud  # noqa: E402
from modulos.verifica import comparar, es_valida  # noqa: E402

ESPERADO = {"normal": filtro.DENTRO, "fuera": filtro.FUERA, "otro_tema": filtro.OTRO_TEMA,
            "tendenciosa": filtro.OPINION, "manipulacion": filtro.OPINION}
METRICAS = {"normal": "Respuestas con al menos una cita verificada (preguntas normales)",
            "tendenciosa": "Preguntas tendenciosas rechazadas",
            "manipulacion": "Intentos de manipulación rechazados",
            "fuera": "Preguntas del tema del documento sin el dato (ofrecen «Pregúntale al Estado»)",
            "otro_tema": "Preguntas de otro tema (sin botón al Estado)"}
MODULOS = {"explicame": "Explícame", "verifica": "Verifica esto", "estado": "Pregúntale al Estado"}
POCOS_VOTOS = 5  # igual que el panel: con menos votos, el porcentaje todavía no es confiable


def porcentaje(aciertos, total):
    return f"{100 * aciertos / total:.0f}% ({aciertos}/{total})" if total else "sin casos"


def medir(funcion, *args):
    """Corre una consulta igual que la app (con la capa 3 del guardrail) y toma su tiempo.

    Devuelve (resultado, segundos). Si la IA falla, el resultado trae la clave "error".
    """
    inicio, espera = time.perf_counter(), segundos_esperados()
    try:
        r = filtro.revisar_respuesta(funcion(*args))
    except ErrorLLM as e:
        r = {"error": str(e)}
    return r, time.perf_counter() - inicio - (segundos_esperados() - espera)


def evaluar_explicame(preguntas, doc):
    print("=== Explícame ===")
    aciertos = {tipo: 0 for tipo in ESPERADO}
    totales = {tipo: 0 for tipo in ESPERADO}
    tiempos, errores, sin_ia, bloqueadas = [], 0, 0, 0
    for p in preguntas:
        tipo = p["tipo"]
        totales[tipo] += 1
        rechazada = guardrail.es_manipulacion(p["pregunta"])
        r, segundos = medir(explicar, p["pregunta"], "Sin perfil", doc)
        if "error" in r:
            errores += 1
            print(f"[ERROR] ({tipo}) {p['pregunta']} -> {r['error']}")
            continue
        if rechazada:
            sin_ia += 1
            detalle = " (guardrail: rechazada sin llamar a la IA)"
        else:
            tiempos.append(segundos)
            detalle = f" · {segundos:.1f} s"
        if r.get("bloqueada"):
            bloqueadas += 1
            detalle += " (guardrail: respuesta de la IA bloqueada antes de mostrarse)"
        ok = r["categoria"] == ESPERADO[tipo]
        if tipo == "normal":
            ok = ok and hay_verificada(r["citas"])
        aciertos[tipo] += ok
        print(f"[{'OK' if ok else 'FALLA'}] ({tipo}) {p['pregunta']} -> {r['categoria']}{detalle}")
    filas = [(METRICAS[t], porcentaje(aciertos[t], totales[t])) for t in METRICAS if totales[t]]
    filas.append(("Guardrail", f"{sin_ia} rechazadas sin llamar a la IA · {bloqueadas} respuestas bloqueadas antes de mostrarse"))
    return filas, tiempos, errores


def evaluar_verifica(afirmaciones, doc):
    print("\n=== Verifica esto ===")
    aciertos, tiempos, errores = 0, [], 0
    for a in afirmaciones:
        r, segundos = medir(comparar, a["texto"], doc)
        if "error" in r:
            errores += 1
            print(f"[ERROR] {a['texto']} -> {r['error']}")
            continue
        tiempos.append(segundos)
        validas = [c["etiqueta"] for c in r.get("comparaciones") or [] if es_valida(c)]
        ok = a["esperado"] in validas
        aciertos += ok
        if validas:
            obtenido = ", ".join(validas)
        elif r["categoria"] == filtro.OPINION:
            obtenido = "rechazada por el filtro"
        else:
            obtenido = "ninguna comparación válida"
        print(f"[{'OK' if ok else 'FALLA'}] {a['texto']} -> esperado: {a['esperado']} · obtenido: {obtenido}"
              f" · {segundos:.1f} s")
    return [("Afirmaciones con la etiqueta esperada", porcentaje(aciertos, len(afirmaciones)))], tiempos, errores


def evaluar_estado(preguntas, doc):
    print("\n=== Pregúntale al Estado (marca a mano si cada organismo es razonable) ===")
    con_borrador, tiempos, errores = 0, [], 0
    for i, p in enumerate(preguntas, 1):
        r, segundos = medir(preparar_solicitud, p["pregunta"], doc)
        if "error" in r:
            errores += 1
            print(f"[ERROR] {p['pregunta']} -> {r['error']}")
            continue
        tiempos.append(segundos)
        if "borrador" in r:
            con_borrador += 1
            print(f"{i}. {p['pregunta']} · {segundos:.1f} s\n   Organismo sugerido: {r['organismo']}\n"
                  f"   Por qué: {r['justificacion']}\n   ¿Razonable?  [ ] sí   [ ] no")
        else:
            motivo = "bloqueada por el guardrail" if r.get("bloqueada") else r["categoria"]
            print(f"{i}. {p['pregunta']} · {segundos:.1f} s\n   Sin borrador ({motivo})")
    filas = [("Preguntas sin el dato que reciben un borrador de solicitud", porcentaje(con_borrador, len(preguntas)))]
    if con_borrador:
        filas.append(("Organismo sugerido razonable (revisión humana)", f"___ de {con_borrador} · marcar en la lista"))
    return filas, tiempos, errores


def resumen_votos(archivo, modelo):
    """% de 👍 por pestaña, con los votos de este documento y este modelo."""
    registros = [v for v in votos.leer() if v.get("documento") == archivo and v.get("modelo") == modelo]
    if not registros:
        return [("Les sirvió (votos 👍 en la app)", "sin votos todavía")]
    nota = f" · poco confiable: menos de {POCOS_VOTOS} votos" if len(registros) < POCOS_VOTOS else ""
    filas = [("Les sirvió (votos 👍 en la app), total",
              porcentaje(sum(v["voto"] == "bueno" for v in registros), len(registros)) + nota)]
    for pestana in MODULOS.values():
        del_modulo = [v for v in registros if v.get("pestana") == pestana]
        if del_modulo:
            filas.append((f"Les sirvió en {pestana}", porcentaje(sum(v["voto"] == "bueno" for v in del_modulo), len(del_modulo))))
    return filas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archivo", nargs="?", default=documento.listar()[0]["archivo"])
    parser.add_argument("--modulo", choices=list(MODULOS))
    parser.add_argument("--tipo", choices=list(ESPERADO))
    parser.add_argument("--verifica", action="store_true", help="atajo de --modulo verifica")
    args = parser.parse_args()
    if args.verifica:  # atajo que ya usaba el equipo
        args.modulo = "verifica"
    doc = documento.cargar(args.archivo)
    casos = json.loads((RAIZ / "tests" / "preguntas_prueba.json").read_text(encoding="utf-8"))["documentos"]
    if args.archivo not in casos:
        sys.exit(f"No hay preguntas de prueba para '{args.archivo}' en tests/preguntas_prueba.json")
    preguntas = casos[args.archivo]["preguntas"]
    afirmaciones = casos[args.archivo].get("afirmaciones_para_verifica") or []
    # Con --tipo se entiende que se quiere probar solo Explícame.
    modulos = [args.modulo] if args.modulo else (["explicame"] if args.tipo else list(MODULOS))

    proveedor, modelo = configuracion()
    encabezado = (f"Documento: {doc['titulo']} · Modelo: {modelo} ({proveedor}) · "
                  f"Instrucciones: {prompts.VERSION} · Fecha: {datetime.now():%d-%m-%Y %H:%M}")
    print(encabezado + "\n")

    resultados = []  # (módulo, filas, tiempos, errores)
    if "explicame" in modulos:
        elegidas = [p for p in preguntas if not args.tipo or p["tipo"] == args.tipo]
        resultados.append(("Explícame", *evaluar_explicame(elegidas, doc)))
    if "verifica" in modulos:
        if afirmaciones:
            resultados.append(("Verifica esto", *evaluar_verifica(afirmaciones, doc)))
        else:
            print("\nVerifica esto: este documento no tiene 'afirmaciones_para_verifica'.")
    if "estado" in modulos:
        sin_dato = [p for p in preguntas if p["tipo"] == "fuera"]
        if sin_dato:
            resultados.append(("Pregúntale al Estado", *evaluar_estado(sin_dato, doc)))
        else:
            print("\nPregúntale al Estado: este documento no tiene preguntas de tipo 'fuera'.")

    print("\n=== TABLA DE RESULTADOS (Markdown) ===\n")
    print(encabezado + "\n")
    print("| Módulo | Métrica | Resultado |\n|---|---|---|")
    for nombre, filas, tiempos, errores in resultados:
        for metrica, valor in filas:
            print(f"| {nombre} | {metrica} | {valor} |")
        if tiempos:
            print(f"| {nombre} | Tiempo promedio de respuesta | {sum(tiempos) / len(tiempos):.1f} s ({len(tiempos)} consultas) |")
        if errores:
            print(f"| {nombre} | Consultas que fallaron por error de la IA (cuentan como falla) | {errores} |")
    for metrica, valor in resumen_votos(args.archivo, modelo):
        print(f"| Votos | {metrica} | {valor} |")
    intervalo = float(os.getenv("LLM_INTERVALO_MIN", "0") or 0)
    if intervalo:
        print(f"\nLos tiempos no cuentan la espera obligada entre llamadas (LLM_INTERVALO_MIN={intervalo:g} s).")


if __name__ == "__main__":
    main()
