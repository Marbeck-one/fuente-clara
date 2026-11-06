from core.citas import hay_verificada, normalizar, verificar

TEXTO_1 = "La ley regula el uso de celulares en los establecimientos educacionales del país."
TEXTO_2 = "Los colegios deberán informar a los apoderados sobre las nuevas reglas de convivencia escolar."
TEXTO_LARGO = " ".join(f"palabra{i}" for i in range(1, 42))


def _doc(*textos):
    fragmentos = [
        {"articulo": f"Artículo {i}", "pagina": i, "texto": texto, "norm": normalizar(texto)}
        for i, texto in enumerate(textos, start=1)
    ]
    return {"fragmentos": fragmentos, "texto_norm": " ".join(f["norm"] for f in fragmentos)}


def test_normalizar_quita_tildes_comillas_y_espacios():
    assert normalizar("Artículo 2°.- “El  alumno”") == "articulo 2°.- el alumno"


def test_cita_real_se_verifica_y_corrige_articulo_y_pagina():
    doc = _doc(TEXTO_1)
    r = verificar([{"articulo": "9", "pagina": 99, "texto_literal": TEXTO_1}], doc)
    assert r[0]["verificada"] is True
    assert r[0]["articulo"] == "Artículo 1"
    assert r[0]["pagina"] == 1


def test_cita_real_con_comillas_y_sin_tildes_se_verifica():
    doc = _doc("Artículo 2°.- El alumno podrá usar el celular con autorización del profesor.")
    cita = "“articulo 2°.- el alumno podra usar el celular con autorizacion del profesor”"
    assert verificar([{"texto_literal": cita}], doc)[0]["verificada"] is True


def test_cita_de_menos_de_8_palabras_se_rechaza():
    doc = _doc(TEXTO_1)
    corta = " ".join(TEXTO_1.split()[:7])
    assert len(corta.split()) == 7
    assert verificar([{"texto_literal": corta}], doc)[0]["verificada"] is False


def test_cita_de_mas_de_40_palabras_se_rechaza():
    doc = _doc(TEXTO_LARGO)
    assert len(TEXTO_LARGO.split()) == 41
    assert verificar([{"texto_literal": TEXTO_LARGO}], doc)[0]["verificada"] is False


def test_cita_inventada_se_rechaza():
    doc = _doc(TEXTO_1)
    r = verificar([{"texto_literal": "los alumnos podrán usar drones durante el recreo"}], doc)
    assert r[0]["verificada"] is False


def test_cita_que_cruza_dos_fragmentos_se_rechaza():
    doc = _doc(TEXTO_1, TEXTO_2)
    # Existe en el texto concatenado, pero no dentro de un solo artículo.
    cruzada = "establecimientos educacionales del país. Los colegios deberán informar"
    assert normalizar(cruzada) in doc["texto_norm"]
    assert verificar([{"texto_literal": cruzada}], doc)[0]["verificada"] is False


def test_citas_invalidas_no_rompen():
    doc = _doc(TEXTO_1)
    assert verificar(None, doc) == []
    assert verificar([{"texto_literal": ""}, "no es dict"], doc)[0]["verificada"] is False


def test_hay_verificada():
    assert hay_verificada([{"verificada": False}, {"verificada": True}]) is True
    assert hay_verificada([{"verificada": False}]) is False
    assert hay_verificada([]) is False
