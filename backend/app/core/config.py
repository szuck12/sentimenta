# backend/app/core/config.py
# Application configuration loaded from environment variables / .env

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the Sentimenta API.

    Values are read from environment variables (optionally a ``.env``
    file) using the ``SENTIMENTA_`` prefix, e.g.
    ``SENTIMENTA_MAX_TEXT_CHARS=2000``.

    Attributes:
        app_name: Human-readable service name used in docs/health.
        version: Current release version, mirrored from CHANGELOG.md.
        cors_origins: Origins allowed by the CORS middleware.
        max_text_chars: Maximum accepted input length in characters,
            enforced identically by the frontend counter.
        min_text_chars: Minimum accepted input length after trimming.
        emotion_threshold: Minimum sigmoid probability for an emotion
            to be listed as "detected" alongside the primary emotion.
        sentence_limit: Maximum number of sentences analyzed in
            sentence-level mode (bounds inference latency).
        enable_attribution: Master switch for Captum token
            attribution. When disabled the explanation falls back to
            probability-based evidence only.
        attribution_steps: Number of integrated-gradient steps; higher
            values are more accurate but slower.
        attribution_max_tokens: Token sequences are truncated to this
            length before attribution to bound its cost.
        model_id: Hugging Face model identifier for the GoEmotions
            classifier.
        device: Torch device string ("cpu" or "mps"); empty selects
            automatically.
        log_level: Uvicorn/loguru-free stdlib logging level.
    """

    model_config = SettingsConfigDict(
        env_prefix="SENTIMENTA_", env_file=".env", extra="ignore"
    )

    app_name: str = "Sentimenta API"
    version: str = "1.1.0"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    max_text_chars: int = 2000
    min_text_chars: int = 1

    emotion_threshold: float = 0.30
    sentence_limit: int = 10

    enable_attribution: bool = True
    attribution_steps: int = 16
    attribution_max_tokens: int = 128

    model_id: str = "SamLowe/roberta-base-go_emotions"
    device: str = ""

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
