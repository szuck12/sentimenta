# backend/tests/unit/test_config.py
# Settings defaults, environment overrides, and validation behaviour.

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


def test_settings_defaults() -> None:
    settings = Settings()
    assert settings.version == "1.3.0"
    assert settings.model_id == "SamLowe/roberta-base-go_emotions"
    assert len(settings.model_revision) == 40
    assert all(c in "0123456789abcdef" for c in settings.model_revision)
    assert settings.emotion_threshold == 0.30
    assert settings.max_text_chars == 2000
    assert settings.sentence_limit == 10
    assert settings.enable_attribution is True
    assert settings.attribution_steps == 16
    assert settings.enable_docs is False
    assert settings.rate_limit == "30/minute"


def test_environment_overrides(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("SENTIMENTA_EMOTION_THRESHOLD", "0.5")
    monkeypatch.setenv(
        "SENTIMENTA_CORS_ORIGINS", '["https://example.test"]'
    )
    monkeypatch.setenv("SENTIMENTA_MAX_TEXT_CHARS", "500")
    monkeypatch.setenv("SENTIMENTA_RATE_LIMIT", "100/hour")
    settings = Settings()
    assert settings.emotion_threshold == 0.5
    assert settings.cors_origins == ["https://example.test"]
    assert settings.max_text_chars == 500
    assert settings.rate_limit == "100/hour"


def test_attribution_steps_rejects_negative() -> None:
    with pytest.raises(ValidationError):
        Settings(attribution_steps=-1)


def test_attribution_steps_rejects_over_32() -> None:
    with pytest.raises(ValidationError):
        Settings(attribution_steps=33)


def test_sentence_limit_rejects_zero() -> None:
    with pytest.raises(ValidationError):
        Settings(sentence_limit=0)


def test_sentence_limit_rejects_over_20() -> None:
    with pytest.raises(ValidationError):
        Settings(sentence_limit=21)


def test_cors_wildcard_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(cors_origins=["*"])


def test_cors_wildcard_with_spaces_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(cors_origins=["  *  "])


def test_cors_valid_origin_accepted() -> None:
    settings = Settings(cors_origins=["https://example.test"])
    assert settings.cors_origins == ["https://example.test"]


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
