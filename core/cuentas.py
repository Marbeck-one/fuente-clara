"""Cuentas opcionales: lo mínimo para dar más consultas a quien entra y medir el uso.

Se guarda un identificador seudónimo (HMAC de la identidad que entrega el proveedor), las fechas de
ingreso y conteos de consultas por día y módulo. Nunca se guardan correo, nombre, tokens ni lo que la
persona escribe, y los votos (core/votos.py) no se ligan a la cuenta.

Con AUTH_MOCK=1 no hay proveedor real: es un usuario simulado para la demo, con su propio archivo.
El archivo está en .gitignore: nunca se sube al repositorio.
"""
import hashlib
import hmac
import os
import sqlite3
import time
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path

ANONIMO = "anonimo"  # en uso_diario: consultas sin cuenta, sumadas, sin nada que las distinga entre sí
RETENCION_DIAS = 90
_CARPETA = Path(__file__).resolve().parents[1] / "data" / "cuentas"
_ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (usuario_id TEXT PRIMARY KEY, proveedor TEXT NOT NULL,
                                     primer_ingreso TEXT NOT NULL, ultimo_ingreso TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS recientes (usuario_id TEXT NOT NULL, momento REAL NOT NULL);
CREATE TABLE IF NOT EXISTS uso_diario (usuario_id TEXT NOT NULL, dia TEXT NOT NULL, modulo TEXT NOT NULL,
                                       consultas INTEGER NOT NULL, PRIMARY KEY (usuario_id, dia, modulo));
"""


def es_mock():
    return os.getenv("AUTH_MOCK") == "1"


def _archivo():
    return Path(os.getenv("CUENTAS_ARCHIVO") or _CARPETA / ("cuentas_demo.db" if es_mock() else "cuentas.db"))


def _conectar():
    archivo = _archivo()
    archivo.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(archivo)
    con.executescript(_ESQUEMA)
    return con


def seudonimo(emisor, sujeto, secreto):
    """Identificador estable de una persona, que sin el secreto no se puede ligar a su cuenta del proveedor."""
    return hmac.new(secreto.encode(), f"{emisor}|{sujeto}".encode(), hashlib.sha256).hexdigest()


def _purgar(con):
    """Aplica la retención: lo que lleva más de RETENCION_DIAS sin uso se elimina."""
    limite = date.today() - timedelta(days=RETENCION_DIAS)
    con.execute("DELETE FROM usuarios WHERE ultimo_ingreso < ?", (limite.isoformat(),))
    con.execute("DELETE FROM uso_diario WHERE dia < ?", (limite.isoformat(),))


def ingresar(usuario_id, proveedor):
    """Registra el ingreso. El primero crea la cuenta: no hay un registro aparte."""
    ahora = datetime.now().isoformat(timespec="seconds")
    with closing(_conectar()) as con, con:
        _purgar(con)
        con.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?) "
                    "ON CONFLICT (usuario_id) DO UPDATE SET ultimo_ingreso = excluded.ultimo_ingreso",
                    (usuario_id, proveedor, ahora, ahora))


def momentos(usuario_id, ventana):
    """Momentos de consulta dentro de la ventana (segundos). Lo anterior ya no sirve y se elimina."""
    desde = time.time() - ventana
    with closing(_conectar()) as con, con:
        con.execute("DELETE FROM recientes WHERE momento < ?", (desde,))
        filas = con.execute("SELECT momento FROM recientes WHERE usuario_id = ? ORDER BY momento", (usuario_id,))
        return [fila[0] for fila in filas]


def agregar_momento(usuario_id, momento):
    with closing(_conectar()) as con, con:
        con.execute("INSERT INTO recientes VALUES (?, ?)", (usuario_id, momento))


def contar_consulta(usuario_id, modulo):
    """Suma una consulta al día y módulo. usuario_id=None la cuenta como anónima."""
    with closing(_conectar()) as con, con:
        con.execute("INSERT INTO uso_diario VALUES (?, ?, ?, 1) "
                    "ON CONFLICT (usuario_id, dia, modulo) DO UPDATE SET consultas = consultas + 1",
                    (usuario_id or ANONIMO, date.today().isoformat(), modulo))


def borrar(usuario_id):
    """Elimina todo lo de esta persona. Lo llama el botón «Borrar mis datos»."""
    with closing(_conectar()) as con, con:
        for tabla in ("usuarios", "recientes", "uso_diario"):
            con.execute(f"DELETE FROM {tabla} WHERE usuario_id = ?", (usuario_id,))


def resumen(dias_activos=7):
    """Números agregados para el panel. Ninguno permite identificar a una persona."""
    desde = (date.today() - timedelta(days=dias_activos - 1)).isoformat()
    with closing(_conectar()) as con:
        uno = lambda sql, *args: con.execute(sql, args).fetchone()[0] or 0  # noqa: E731
        return {
            "cuentas": uno("SELECT COUNT(*) FROM usuarios"),
            "activas": uno("SELECT COUNT(DISTINCT usuario_id) FROM uso_diario WHERE usuario_id != ? AND dia >= ?",
                           ANONIMO, desde),
            "volvieron": uno("SELECT COUNT(*) FROM (SELECT usuario_id FROM uso_diario WHERE usuario_id != ? "
                             "GROUP BY usuario_id HAVING COUNT(DISTINCT dia) > 1)", ANONIMO),
            "con_cuenta": uno("SELECT SUM(consultas) FROM uso_diario WHERE usuario_id != ?", ANONIMO),
            "sin_cuenta": uno("SELECT SUM(consultas) FROM uso_diario WHERE usuario_id = ?", ANONIMO),
            "por_modulo": dict(con.execute("SELECT modulo, SUM(consultas) FROM uso_diario GROUP BY modulo")),
        }
