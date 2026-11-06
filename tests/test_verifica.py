from modulos import verifica


def test_comparar_corta_opinion_sin_llamar_al_modelo(monkeypatch):
    monkeypatch.setattr(verifica.filtro, "clasificar", lambda *a, **k: verifica.filtro.OPINION)
    monkeypatch.setattr(verifica, "complete", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no llamar")))
    assert verifica.comparar("texto", {}) == {"categoria": verifica.filtro.OPINION}


def test_comparar_corta_otro_tema_sin_llamar_al_modelo(monkeypatch):
    monkeypatch.setattr(verifica.filtro, "clasificar", lambda *a, **k: verifica.filtro.OTRO_TEMA)
    monkeypatch.setattr(verifica, "complete", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no llamar")))
    assert verifica.comparar("texto", {}) == {"categoria": verifica.filtro.OTRO_TEMA}
