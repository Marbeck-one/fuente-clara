"""Límite de uso: evita que alguien gaste la cuota de la API repitiendo consultas.

Dos topes, configurables en .env:
- por persona (sesión): LIMITE_CONSULTAS_SESION consultas cada LIMITE_VENTANA_MIN minutos;
- para toda la app: LIMITE_CONSULTAS_MINUTO consultas por minuto.
No se limita por dirección IP: en un evento todos comparten el mismo wifi.
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


def permitir(historial_sesion):
    """Registra una consulta si cabe en los topes. Devuelve None si se permite, o SESION / GLOBAL si no.

    historial_sesion: lista de momentos de consulta de esta persona (vive en st.session_state).
    """
    ahora = time.time()
    ventana = _entero("LIMITE_VENTANA_MIN", 10) * 60
    historial_sesion[:] = [t for t in historial_sesion if ahora - t < ventana]
    if len(historial_sesion) >= _entero("LIMITE_CONSULTAS_SESION", 20):
        return SESION
    with _candado:
        while _recientes and ahora - _recientes[0] >= 60:
            _recientes.popleft()
        if len(_recientes) >= _entero("LIMITE_CONSULTAS_MINUTO", 30):
            return GLOBAL
        _recientes.append(ahora)
    historial_sesion.append(ahora)
    return None
