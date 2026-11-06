"""Prueba real de lectura de capturas en "Verifica esto".

Genera una captura sintética en memoria (no la guarda), extrae su texto con el modelo
configurado y comprueba que llega a la misma comparación que el texto pegado.

Uso:  python scripts/probar_imagen.py
Consume aproximadamente 5 solicitudes a la API. No imprime ni guarda la clave.
"""
import sys
import textwrap
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from core import documento, filtro  # noqa: E402
from core.citas import hay_verificada  # noqa: E402
from core.llm import ErrorLLM  # noqa: E402
from modulos.verifica import comparar, extraer_texto  # noqa: E402

AFIRMACION = "La ley permite usar el celular durante las clases a todos los estudiantes."


def _fuente():
    """Usa una fuente con tildes claras; si no existe, cae a la fuente por defecto."""
    for ruta in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/TTF/DejaVuSans.ttf"):
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, 40)
    try:
        return ImageFont.load_default(size=40)
    except TypeError:  # Pillow antiguo sin tamaño en la fuente por defecto
        return ImageFont.load_default()


def captura(texto):
    """Crea una imagen tipo captura, solo en memoria."""
    imagen = Image.new("RGB", (1080, 760), "white")
    dibujo = ImageDraw.Draw(imagen)
    fuente = _fuente()
    y = 70
    for linea in textwrap.wrap(texto, width=40):
        dibujo.text((60, y), linea, fill="black", font=fuente)
        y += 58
    return imagen


def _etiquetas(resultado):
    return [c.get("etiqueta") for c in resultado.get("comparaciones") or []]


def _citas_verificadas(resultado):
    return sum(hay_verificada(c.get("citas") or []) for c in resultado.get("comparaciones") or [])


def main():
    catalogo = documento.listar()
    if not catalogo:
        sys.exit("No hay documentos en el catálogo.")
    doc = documento.cargar(catalogo[0]["archivo"])
    print(f"Documento: {doc['titulo']}\n")

    imagen = captura(AFIRMACION)
    inicio = time.time()
    try:
        extraido = extraer_texto(imagen)
    except ErrorLLM as e:
        sys.exit(f"[FALLA] no se pudo leer la imagen: {e}")

    print(f"[OK] texto extraído ({time.time() - inicio:.1f}s): {extraido[:180]!r}")
    faltan = [p for p in ("celular", "clases", "estudiantes") if p not in extraido.lower()]
    if faltan:
        sys.exit(f"[FALLA] faltan palabras clave en la transcripción: {faltan}")
    print("[OK] la transcripción contiene las palabras clave")

    try:
        desde_imagen = filtro.revisar_respuesta(comparar(extraido, doc))
        desde_texto = filtro.revisar_respuesta(comparar(AFIRMACION, doc))
    except ErrorLLM as e:
        sys.exit(f"[FALLA] falló la comparación: {e}")

    etiquetas_imagen = _etiquetas(desde_imagen)
    etiquetas_texto = _etiquetas(desde_texto)
    print(f"[{'OK' if etiquetas_imagen else 'FALLA'}] comparación desde imagen: {etiquetas_imagen}")
    print(f"[{'OK' if etiquetas_texto else 'FALLA'}] comparación desde texto pegado: {etiquetas_texto}")

    misma = etiquetas_imagen == etiquetas_texto and bool(etiquetas_imagen)
    print(f"[{'OK' if misma else 'FALLA'}] misma etiqueta que el texto pegado")
    citas = _citas_verificadas(desde_imagen)
    print(f"[{'OK' if citas else 'FALLA'}] citas verificadas desde la imagen: {citas}")

    ok = misma and citas > 0
    print("\nPrueba de imagen OK" if ok else "\nLa prueba de imagen falló")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
