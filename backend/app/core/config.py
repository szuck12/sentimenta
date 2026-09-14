# backend/app/core/config.py
# Application configuration loaded from environment variables / .env

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .ratelimit import parse_rate_limit


class Settings(BaseSettings):
    """Runtime settings for the Sentimenta API.

    Values are read from environment variables (optionally a ``.env``
    file) using the ``SENTIMENTA_`` prefix, e.g.
    ``SENTIMENTA_MAX_TEXT_CHARS=2000``.

    Attributes:
        app_name: Human-readable service name used in docs/health.
        version: Current release version, mirrored from CHANGELOG.md.
        cors_origins: Origins allowed by the CORS middleware.  Wildcard
            origins are rejected.
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
            values are more accurate but slower.  Capped at 32.
        attribution_max_tokens: Token sequences are truncated to this
            length before attribution to bound its cost.
        model_id: Hugging Face model identifier for the GoEmotions
            classifier.
        model_revision: Immutable commit revision of the model
            repository. Pinning to a specific revision prevents a
            mutable upstream tag from silently changing the weights
            that are loaded.
        device: Torch device string ("cpu" or "mps"); empty selects
            automatically.
        enable_docs: Whether to expose the interactive API docs
            (``/docs``, ``/redoc``) and the OpenAPI schema.  Disabled
            by default to reduce the exposed surface.
        rate_limit: Per-IP rate limit (e.g. ``'30/minute'``).  Set
            to ``'0'`` or leave blank to disable.
        trust_proxy: When True, derive the client IP from
            ``X-Forwarded-For``/``X-Real-IP``.  Only enable behind a
            trusted reverse proxy that overwrites these headers.
        max_body_bytes: Maximum accepted request body size in bytes.
            Larger requests are rejected with HTTP 413.
        max_concurrent_requests: Maximum number of concurrent analysis
            requests; additional requests queue briefly and then fail
            with HTTP 503.
        max_queue_wait_seconds: How long a request waits for a free
            concurrency slot before being rejected.
        model_sha256: Expected SHA-256 of the model weights file.  When
            set, the downloaded weights are verified before loading.
        log_level: Uvicorn/loguru-free stdlib logging level.
    """

    model_config = SettingsConfigDict(
        env_prefix="SENTIMENTA_", env_file=".env", extra="ignore"
    )

    app_name: str = "Sentimenta API"
    version: str = "1.3.1"

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
    model_revision: str = "d75048347613a25d77de8cf6412eaae9fa7b26be"
    model_sha256: str = (
        "84d6d338b4cf63f0ed3c990a0ce748d32d1d2965c072f4645accaa71af3888c0"
    )
    device: str = ""

    enable_docs: bool = False

    rate_limit: str = "30/minute"
    trust_proxy: bool = False
    max_body_bytes: int = 65536
    max_concurrent_requests: int = 4
    max_queue_wait_seconds: float = 5.0

    log_level: str = "INFO"

    @field_validator("attribution_steps")
    @classmethod
    def _validate_attribution_steps(cls, v: int) -> int:
        if v < 0 or v > 32:
            raise ValueError(
                f"attribution_steps must be between 0 and 32, got {v}"
            )
        return v

    @field_validator("sentence_limit")
    @classmethod
    def _validate_sentence_limit(cls, v: int) -> int:
        if v < 1 or v > 20:
            raise ValueError(
                f"sentence_limit must be between 1 and 20, got {v}"
            )
        return v

    @field_validator("cors_origins")
    @classmethod
    def _reject_wildcard_cors(cls, v: list[str]) -> list[str]:
        for origin in v:
            if origin.strip() == "*":
                raise ValueError(
                    "CORS wildcard '*' is not allowed. "
                    "Use explicit origins instead."
                )
        return v

    @field_validator("rate_limit")
    @classmethod
    def _validate_rate_limit(cls, v: str) -> str:
        try:
            parse_rate_limit(v)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        return v


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
