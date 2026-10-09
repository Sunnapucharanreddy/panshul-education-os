from app.core.config import Settings


def test_environment_defaults_to_production_when_unset(monkeypatch):
    monkeypatch.delenv("ENV", raising=False)

    settings = Settings(_env_file=None)

    assert settings.env == "production"
