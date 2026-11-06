import pytest

from core import llm


@pytest.fixture(autouse=True)
def ia_limpia(monkeypatch):
    """Cada prueba parte sin cadena de modelos (aunque el .env local tenga una), sin pausas
    y sin un «último modelo» que haya dejado otra prueba."""
    monkeypatch.delenv("LLM_CADENA", raising=False)
    llm._pausas.clear()
    llm._hilo.ultimo = None
    yield
    llm._pausas.clear()
    llm._hilo.ultimo = None


@pytest.fixture(autouse=True)
def cuentas_aisladas(monkeypatch, tmp_path):
    """Las pruebas no tocan datos reales ni dependen del .env de quien las corre."""
    monkeypatch.setenv("CUENTAS_ARCHIVO", str(tmp_path / "cuentas.db"))
    monkeypatch.setenv("AUTH_MOCK", "0")
    monkeypatch.setenv("CUENTAS_SECRETO", "")
