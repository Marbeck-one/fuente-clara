"""Almacenamiento de cuentas: qué se guarda, qué no, y que se pueda borrar."""
import sqlite3
import time
from datetime import date, timedelta

from core import cuentas


def _filas(tabla):
    with sqlite3.connect(cuentas._archivo()) as con:
        return con.execute(f"SELECT * FROM {tabla}").fetchall()


def test_seudonimo_es_estable_y_depende_del_secreto():
    a = cuentas.seudonimo("https://accounts.google.com", "123", "secreto")
    assert a == cuentas.seudonimo("https://accounts.google.com", "123", "secreto")
    assert a != cuentas.seudonimo("https://accounts.google.com", "123", "otro")
    assert a != cuentas.seudonimo("https://accounts.google.com", "124", "secreto")
    assert "123" not in a


def test_primer_ingreso_crea_la_cuenta_y_los_siguientes_no_la_duplican():
    cuentas.ingresar("u1", "mock")
    primer = _filas("usuarios")[0][2]
    cuentas.ingresar("u1", "mock")
    filas = _filas("usuarios")
    assert len(filas) == 1
    assert filas[0][2] == primer
    assert cuentas.resumen()["cuentas"] == 1


def test_solo_se_guardan_las_columnas_previstas():
    """Si alguien agrega correo, nombre o texto a una tabla, esta prueba obliga a revisar la promesa de privacidad."""
    cuentas.ingresar("u1", "mock")
    columnas = {}
    with sqlite3.connect(cuentas._archivo()) as con:
        for tabla in ("usuarios", "recientes", "uso_diario"):
            columnas[tabla] = [c[1] for c in con.execute(f"PRAGMA table_info({tabla})")]
    assert columnas == {"usuarios": ["usuario_id", "proveedor", "primer_ingreso", "ultimo_ingreso"],
                        "recientes": ["usuario_id", "momento"],
                        "uso_diario": ["usuario_id", "dia", "modulo", "consultas"]}


def test_momentos_sobreviven_entre_lecturas_y_expiran_con_la_ventana():
    ahora = time.time()
    cuentas.agregar_momento("u1", ahora)
    cuentas.agregar_momento("u1", ahora - 1000)
    cuentas.agregar_momento("u2", ahora)
    assert cuentas.momentos("u1", 600) == [ahora]


def test_contar_consulta_suma_por_dia_y_modulo_y_separa_a_los_anonimos():
    cuentas.contar_consulta("u1", "Explícame")
    cuentas.contar_consulta("u1", "Explícame")
    cuentas.contar_consulta(None, "Explícame")
    cuentas.contar_consulta(None, "Verifica esto")
    datos = cuentas.resumen()
    assert datos["con_cuenta"] == 2
    assert datos["sin_cuenta"] == 2
    assert datos["por_modulo"] == {"Explícame": 3, "Verifica esto": 1}
    assert datos["activas"] == 1


def test_borrar_elimina_todo_lo_de_esa_persona_y_nada_mas():
    for uid in ("u1", "u2"):
        cuentas.ingresar(uid, "mock")
        cuentas.agregar_momento(uid, time.time())
        cuentas.contar_consulta(uid, "Explícame")
    cuentas.borrar("u1")
    for tabla in ("usuarios", "recientes", "uso_diario"):
        ids = [fila[0] for fila in _filas(tabla)]
        assert ids == ["u2"]


def test_volvieron_cuenta_solo_a_quien_uso_la_app_en_dias_distintos():
    cuentas.contar_consulta("u1", "Explícame")
    cuentas.contar_consulta("u2", "Explícame")
    ayer = (date.today() - timedelta(days=1)).isoformat()
    with sqlite3.connect(cuentas._archivo()) as con:
        con.execute("INSERT INTO uso_diario VALUES ('u1', ?, 'Explícame', 1)", (ayer,))
    assert cuentas.resumen()["volvieron"] == 1


def test_la_retencion_elimina_lo_que_lleva_90_dias_sin_uso():
    viejo = (date.today() - timedelta(days=cuentas.RETENCION_DIAS + 1)).isoformat()
    cuentas.ingresar("activo", "mock")
    with sqlite3.connect(cuentas._archivo()) as con:
        con.execute("INSERT INTO usuarios VALUES ('viejo', 'mock', ?, ?)", (viejo, viejo))
        con.execute("INSERT INTO uso_diario VALUES ('viejo', ?, 'Explícame', 1)", (viejo,))
    cuentas.ingresar("activo", "mock")
    assert [fila[0] for fila in _filas("usuarios")] == ["activo"]
    assert _filas("uso_diario") == []


def test_mock_y_real_no_comparten_archivo(monkeypatch):
    monkeypatch.delenv("CUENTAS_ARCHIVO")
    monkeypatch.setenv("AUTH_MOCK", "1")
    demo = cuentas._archivo()
    monkeypatch.setenv("AUTH_MOCK", "0")
    assert demo != cuentas._archivo()
