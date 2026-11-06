from core import documento

PRINCIPAL = "ley_21801_celulares_en_colegios.pdf"


def test_listar_solo_documentos_existentes_y_sin_el_ficticio():
    docs = documento.listar()
    archivos = {d["archivo"] for d in docs}
    assert PRINCIPAL in archivos
    assert "EJEMPLO_FICTICIO_tarjeta_muevete.txt" not in archivos
    assert all((documento.CARPETA / a).exists() for a in archivos)


def test_cargar_documento_principal():
    doc = documento.cargar(PRINCIPAL)
    assert doc["titulo"].startswith("Ley 21.801")
    assert doc["fragmentos"]
    assert doc["texto_norm"]
    assert all({"articulo", "pagina", "texto", "norm"} <= set(f) for f in doc["fragmentos"])
    assert max(f["pagina"] for f in doc["fragmentos"]) >= 1


def test_fragmentos_separan_por_articulo_y_pagina():
    paginas = [
        "ENCABEZADO REPETIDO\nArtículo 1.- La ley regula el uso de celulares en los colegios.\n"
        "Artículo 2°.- Los establecimientos deberán informar a los apoderados."
    ]
    fragmentos = documento._fragmentos(paginas)
    etiquetas = [f["articulo"] for f in fragmentos]
    assert "Artículo 1" in etiquetas
    assert "Artículo 2" in etiquetas
    assert all(f["pagina"] == 1 for f in fragmentos)


def test_fragmentos_reconocen_numerales_de_ley_modificatoria():
    paginas = ["Artículo único.- Introdúcense las siguientes modificaciones:\n"
               "1. Agrégase en el artículo 3 el siguiente literal.\n"
               "2. En el artículo 10, reemplázase la letra a)."]
    fragmentos = documento._fragmentos(paginas)
    etiquetas = [f["articulo"] for f in fragmentos]
    assert "Artículo único, numeral 1" in etiquetas
    assert "Artículo único, numeral 2" in etiquetas


def test_sin_repetidas_quita_encabezados_de_casi_todas_las_paginas():
    paginas = [
        "Página 1 de 3\nTexto uno",
        "Página 2 de 3\nTexto dos",
        "Página 3 de 3\nTexto tres",
        "Texto cuatro",
    ]
    limpias = documento._sin_repetidas(paginas)
    assert all("Página" not in p for p in limpias[:3])
    assert "Texto cuatro" in limpias[3]


def test_para_prompt_incluye_etiquetas_y_limites():
    doc = documento.cargar(PRINCIPAL)
    prompt = documento.para_prompt(doc)
    assert doc["titulo"] in prompt
    assert "=== INICIO DEL DOCUMENTO ===" in prompt
    assert "=== FIN DEL DOCUMENTO ===" in prompt
    assert "[Encabezado | página 1]" in prompt
