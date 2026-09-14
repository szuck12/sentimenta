# backend/tests/unit/test_config.py
# Settings defaults, environment overrides, and caching behaviour.

from app.core.config import Settings, get_settings


def test_settings_defaults() -> None:
    settings = Settings()
    assert settings.version == "1.1.0"
    assert settings.model_id == "SamLowe/roberta-base-go_emotions"
    assert settings.emotion_threshold == 0.30
    assert settings.max_text_chars == 2000
    assert settings.sentence_limit == 10
    assert settings.enable_attribution is True


def test_environment_overrides(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("SENTIMENTA_EMOTION_THRESHOLD", "0.5")
    monkeypatch.setenv(
        "SENTIMENTA_CORS_ORIGINS", '["https://example.test"]'
    )
    monkeypatch.setenv("SENTIMENTA_MAX_TEXT_CHARS", "500")
    settings = Settings()
    assert settings.emotion_threshold == 0.5
    assert settings.cors_origins == ["https://example.test"]
    assert settings.max_text_chars == 500


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
