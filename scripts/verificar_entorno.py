"""Revisa la configuración antes de la demo, sin exponer secretos.

Uso:
    python scripts/verificar_entorno.py            # solo configuración y documento
    python scripts/verificar_entorno.py --probar   # además hace una llamada mínima a la IA

Sale con código 0 si todo está bien y 1 si falta algo.
"""
import argparse
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

import yaml  # noqa: E402

from core import documento, prompts  # noqa: E402
from core import llm  # noqa: E402
from core.llm import CLAVES, ErrorLLM, cadena, complete, tiene_clave, ultimo_modelo  # noqa: E402


def _si_no(condicion, mensaje, fallos):
    print(f"[{'OK' if condicion else 'FALLA'}] {mensaje}")
    if not condicion:
        fallos.append(mensaje)
    return condicion


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--probar", action="store_true", help="hace una llamada mínima real al modelo")
    args = parser.parse_args()

    fallos = []
    try:
        eslabones = cadena()
    except ErrorLLM as e:
        print(f"[FALLA] configuración: {e}")
        return 1

    proveedor, modelo = eslabones[0]
    print(f"Proveedor: {proveedor}\nModelo: {modelo}\nInstrucciones: {prompts.VERSION}")
    if len(eslabones) > 1:
        print("Respaldo, en orden: " + " → ".join(f"{p}:{m}" for p, m in eslabones[1:]))
    print()

    _si_no(tiene_clave(proveedor), f"clave de API definida ({' o '.join(CLAVES[proveedor])})", fallos)
    for p, m in eslabones[1:]:
        if not tiene_clave(p):  # un respaldo sin clave se salta: no es una falla, pero conviene saberlo
            print(f"[AVISO] respaldo {p}:{m} sin clave ({' o '.join(CLAVES[p])}): se saltará")
    if any(p == "openai" for p, _ in eslabones) and os.getenv("OPENAI_BASE_URL", "").strip():
        print(f"[INFO] OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")

    catalogo = documento.listar()
    if _si_no(bool(catalogo), f"catálogo con documentos ({len(catalogo)})", fallos):
        doc = documento.cargar(catalogo[0]["archivo"])
        _si_no(bool(doc["fragmentos"]), f"documento principal cargado ({len(doc['fragmentos'])} fragmentos)", fallos)

    config = yaml.safe_load((RAIZ / "config" / "transparencia.yaml").read_text(encoding="utf-8"))
    pendientes = [d["texto"][:45] for grupo in ("ley", "portal", "pasos", "plazos", "plantilla")
                  for d in (config[grupo] if isinstance(config[grupo], list) else [config[grupo]])
                  if isinstance(d, dict) and d.get("estado") == "VERIFICAR"]
    if pendientes:
        print(f"[INFO] {len(pendientes)} dato(s) de transparencia aún en VERIFICAR")
    else:
        print("[OK] datos de transparencia verificados")

    if args.probar:
        print("\nProbando una llamada real (consume pocos tokens)…")
        try:
            r = complete("Eres un verificador. Responde solo JSON.", 'Devuelve exactamente {"ok": true}')
            _si_no(r.get("ok") is True, f"la IA respondió ({':'.join(ultimo_modelo())}): {r}", fallos)
        except ErrorLLM as e:
            _si_no(False, f"llamada a la IA: {e}", fallos)
        for p, m in eslabones[1:]:  # cada respaldo por separado, para saber si de verdad sirve
            if not tiene_clave(p):
                continue
            try:
                texto = llm._llamar_proveedor("Responde solo JSON.", 'Devuelve exactamente {"ok": true}',
                                              eslabon=(p, m), reintentos=False)
                print(f"[{'OK' if llm._parsear(texto).get('ok') is True else 'AVISO'}] respaldo {p}:{m} responde")
            except Exception as e:  # un respaldo caído no impide la demo
                print(f"[AVISO] respaldo {p}:{m} no responde: {type(e).__name__} {str(e)[:120]}")

    print(f"\n{'Todo OK' if not fallos else f'{len(fallos)} fallo(s)'}")
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
