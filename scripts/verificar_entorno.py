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
from core.llm import ErrorLLM, complete, configuracion  # noqa: E402

CLAVES = {
    "anthropic": ("ANTHROPIC_API_KEY",),
    "openai": ("OPENAI_API_KEY",),
    "google": ("GOOGLE_API_KEY", "GEMINI_API_KEY"),
}


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
        proveedor, modelo = configuracion()
    except ErrorLLM as e:
        print(f"[FALLA] configuración: {e}")
        return 1

    print(f"Proveedor: {proveedor}\nModelo: {modelo}\nInstrucciones: {prompts.VERSION}\n")

    variables = CLAVES.get(proveedor, ())
    definida = any(os.getenv(v, "").strip() for v in variables)
    _si_no(definida, f"clave de API definida ({' o '.join(variables)})", fallos)
    if proveedor == "openai" and os.getenv("OPENAI_BASE_URL", "").strip():
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
            _si_no(r.get("ok") is True, f"la IA respondió: {r}", fallos)
        except ErrorLLM as e:
            _si_no(False, f"llamada a la IA: {e}", fallos)

    print(f"\n{'Todo OK' if not fallos else f'{len(fallos)} fallo(s)'}")
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
