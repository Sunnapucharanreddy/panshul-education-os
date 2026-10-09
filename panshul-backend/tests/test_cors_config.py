from types import SimpleNamespace

import pytest

import app.main as app_main


def test_debug_development_keeps_local_wildcard_cors(monkeypatch):
    monkeypatch.setattr(
        app_main,
        "settings",
        SimpleNamespace(env="development", debug=True, cors_origins="http://localhost:3000"),
    )

    assert app_main._cors_origins() == ["*"]


def test_production_rejects_debug_mode(monkeypatch):
    monkeypatch.setattr(
        app_main,
        "settings",
        SimpleNamespace(env="production", debug=True, cors_origins="https://school.example"),
    )

    with pytest.raises(RuntimeError, match="DEBUG must be false"):
        app_main._cors_origins()


def test_non_debug_mode_rejects_wildcard_cors(monkeypatch):
    monkeypatch.setattr(
        app_main,
        "settings",
        SimpleNamespace(env="production", debug=False, cors_origins="https://school.example, *"),
    )

    with pytest.raises(RuntimeError, match="CORS_ORIGINS cannot contain"):
        app_main._cors_origins()


def test_non_debug_mode_uses_configured_origins(monkeypatch):
    monkeypatch.setattr(
        app_main,
        "settings",
        SimpleNamespace(env="production", debug=False, cors_origins=" https://school.example,https://admin.example "),
    )

    assert app_main._cors_origins() == ["https://school.example", "https://admin.example"]
