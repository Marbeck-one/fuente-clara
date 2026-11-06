import pytest


@pytest.fixture(autouse=True)
def cuentas_aisladas(monkeypatch, tmp_path):
    """Las pruebas no tocan datos reales ni dependen del .env de quien las corre."""
    monkeypatch.setenv("CUENTAS_ARCHIVO", str(tmp_path / "cuentas.db"))
    monkeypatch.setenv("AUTH_MOCK", "0")
    monkeypatch.setenv("CUENTAS_SECRETO", "")
