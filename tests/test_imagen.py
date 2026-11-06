import io

import pytest
from PIL import Image

from core import prompts
from core.llm import ErrorLLM
from modulos import verifica


def _bytes(imagen, formato="PNG"):
    salida = io.BytesIO()
    imagen.save(salida, format=formato)
    return salida.getvalue()


def _imagen(mode="RGB", size=(120, 80), color="white"):
    return Image.new(mode, size, color)


@pytest.mark.parametrize("formato", ["PNG", "JPEG", "WEBP"])
def test_leer_imagen_acepta_los_formatos_soportados(formato):
    original = _imagen(color="white" if formato == "JPEG" else "red")
    imagen = verifica.leer_imagen(_bytes(original, formato))
    assert imagen.mode == "RGB"
    assert imagen.size == original.size


def test_leer_imagen_rechaza_formatos_no_soportados():
    with pytest.raises(ValueError, match="Formato no compatible"):
        verifica.leer_imagen(_bytes(_imagen(), "GIF"))


def test_leer_imagen_rechaza_archivo_corrupto():
    with pytest.raises(ValueError, match="no es una imagen válida"):
        verifica.leer_imagen(b"esto no es una imagen")


def test_leer_imagen_rechaza_archivo_demasiado_grande():
    with pytest.raises(ValueError, match="supera los 5 MB"):
        verifica.leer_imagen(b"x" * (verifica.MAX_BYTES + 1))


def test_leer_imagen_rechaza_imagen_muy_pequena():
    with pytest.raises(ValueError, match="demasiado pequeña"):
        verifica.leer_imagen(_bytes(_imagen(size=(40, 40))))


def test_leer_imagen_normaliza_transparencia_a_rgb():
    imagen = verifica.leer_imagen(_bytes(_imagen("RGBA", color=(255, 0, 0, 0))))
    assert imagen.mode == "RGB"
    assert imagen.getpixel((0, 0)) == (255, 255, 255)


def test_extraer_texto_envia_la_imagen_y_el_prompt(monkeypatch):
    vista = {}
    imagen = _imagen()

    def falso_complete(system, user, imagen=None):
        vista.update(system=system, user=user, imagen=imagen)
        return {"texto": "  Hola Fuente Clara  "}

    monkeypatch.setattr(verifica, "complete", falso_complete)
    assert verifica.extraer_texto(imagen) == "Hola Fuente Clara"
    assert vista["system"] == prompts.TRANSCRIBIR
    assert vista["imagen"] is imagen
    assert "Transcribe" in vista["user"]


def test_extraer_texto_vacio(monkeypatch):
    monkeypatch.setattr(verifica, "complete", lambda *a, **k: {"texto": "   "})
    assert verifica.extraer_texto(_imagen()) == ""


def test_extraer_texto_propaga_el_error_del_modelo(monkeypatch):
    def falla(*a, **k):
        raise ErrorLLM("sin cuota")

    monkeypatch.setattr(verifica, "complete", falla)
    with pytest.raises(ErrorLLM):
        verifica.extraer_texto(_imagen())
