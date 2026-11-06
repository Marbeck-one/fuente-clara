"""Detección de artículos: una cita con la etiqueta equivocada rompe la trazabilidad, aunque el texto sea real."""
import pytest

from core import documento


def _etiquetas(texto):
    return [documento._etiqueta(m.group(1)) for m in documento.RE_ARTICULO.finditer(texto)]


@pytest.mark.parametrize("linea, esperada", [
    # Los que ya funcionaban
    ("Artículo 1º.- El tratamiento", "Artículo 1"),
    ("Artículo 2°.- Para los efectos", "Artículo 2"),
    ("Artículo 10 bis.- Prohíbese", "Artículo 10 bis"),
    ('"Artículo 10 bis.- Prohíbese', "Artículo 10 bis"),
    ("Artículo 2 ter.- Las normas", "Artículo 2 ter"),
    ("ARTÍCULO ÚNICO. Texto", "Artículo único"),
    ("Artículo único.- Introdúcense", "Artículo único"),
    ("Artículo primero transitorio.- Texto", "Artículo primero transitorio"),
    ("Artículo transitorio.- Texto", "Artículo transitorio"),
    ("Artículo duodécimo.- Texto", "Artículo duodécimo"),
    # Número con letra
    ('"Artículo 211-A.- Las trabajadoras', "Artículo 211-A"),
    ("Artículo 273 A.- Antecedentes", "Artículo 273 A"),
    ("Artículo 17 G.- La carga", "Artículo 17 G"),
    ("Artículo 286 Ñ.- Nueva propuesta", "Artículo 286 Ñ"),
    ("Artículo décimo tercero.- En todas", "Artículo décimo tercero"),
    # El símbolo de grado va antes del bis
    ("Artículo 3° bis.- El consumidor", "Artículo 3 bis"),
    ("Artículo 2º ter.- Texto", "Artículo 2 ter"),
])
def test_reconoce_el_titulo_de_un_articulo(linea, esperada):
    assert _etiquetas(linea) == [esperada]


@pytest.mark.parametrize("linea", [
    "artículo 261. El expediente",   # referencia que quedó al inicio de una línea
    "artículo 58. Los principios",
    "artículo precedente. Sin perjuicio",
    "artículo anterior: texto",
    "Artículo anterior. Texto",
    "Artículo siguiente. Texto",
    "artículo 5 de la ley 19.880",
    "Artículo 19, N° 12, de la Constitución",
    "Artículo 1 La ley señala",
])
def test_no_confunde_referencias_con_titulos(linea):
    assert _etiquetas(linea) == []


def test_una_referencia_al_inicio_de_linea_no_corta_el_articulo():
    pagina = "Artículo 260.- Ámbito de aplicación.\nConforme al\nartículo 261. El expediente será público.\nArtículo 261.- Inicio del procedimiento."
    fragmentos = documento._fragmentos([pagina])
    assert [f["articulo"] for f in fragmentos] == ["Artículo 260", "Artículo 261"]
    assert "El expediente será público" in fragmentos[0]["texto"]


def test_un_articulo_con_letra_o_bis_tiene_su_propio_fragmento():
    pagina = "Artículo 3°.- Son derechos.\nArtículo 3° bis.- Retracto.\nArtículo 211-A.- Protocolo.\nArtículo 211-B.- Principios."
    fragmentos = documento._fragmentos([pagina])
    assert [f["articulo"] for f in fragmentos] == ["Artículo 3", "Artículo 3 bis", "Artículo 211-A", "Artículo 211-B"]
