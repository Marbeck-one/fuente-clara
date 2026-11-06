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
