"""Límite de uso: evita que alguien gaste la cuota de la API repitiendo consultas.

Topes configurables en .env:
- por persona: LIMITE_CONSULTAS_SESION consultas cada LIMITE_VENTANA_MIN minutos;
- sin cuenta, si el login está disponible: LIMITE_CONSULTAS_ANONIMO en esa misma ventana;
- para toda la app: LIMITE_CONSULTAS_MINUTO consultas por minuto.
No se limita por dirección IP: en un evento todos comparten el mismo wifi.

Sin cuenta, el historial vive en la sesión y se reinicia al recargar la página. Con cuenta se guarda
(core/cuentas.py). Por eso el tope sin cuenta es un incentivo, no una barrera: lo que protege la cuota
de la API es el tope global.
"""
import os
import threading
import time
from collections import deque

SESION, GLOBAL = "sesion", "global"
_candado = threading.Lock()
_recientes = deque()  # momentos de las consultas de toda la app en el último minuto


def _entero(nombre, defecto):
    try:
        return int(os.getenv(nombre, "") or defecto)
    except ValueError:
        return defecto


def ventana():
    """Segundos que dura la ventana del tope por persona."""
    return _entero("LIMITE_VENTANA_MIN", 10) * 60


def maximo_persona():
    return _entero("LIMITE_CONSULTAS_SESION", 20)


def maximo_anonimo():
    return _entero("LIMITE_CONSULTAS_ANONIMO", 5)


def permitir(historial, maximo=None):
    """Registra una consulta si cabe en los topes. Devuelve None si se permite, o SESION / GLOBAL si no.

    historial: lista de momentos de consulta de esta persona. maximo: su tope (por defecto, maximo_persona()).
    """
    ahora = time.time()
    historial[:] = [t for t in historial if ahora - t < ventana()]
    if len(historial) >= (maximo_persona() if maximo is None else maximo):
        return SESION
    with _candado:
        while _recientes and ahora - _recientes[0] >= 60:
            _recientes.popleft()
        if len(_recientes) >= _entero("LIMITE_CONSULTAS_MINUTO", 30):
            return GLOBAL
        _recientes.append(ahora)
    historial.append(ahora)
    return None
