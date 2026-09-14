# backend/app/main.py
# FastAPI application factory and startup lifespan that loads the
# emotion model exactly once before accepting requests.

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from .api import routes
from .core.config import Settings, get_settings
from .core.errors import (
    AppError,
    app_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from .services.analysis_service import AnalysisService
from .services.emotion_model_service import EmotionModelService
from .services.explanation_service import ExplanationService

logger = logging.getLogger(__name__)


class _RateLimiter:
    """Simple in-memory sliding-window rate limiter.

    Each key (typically a client IP) gets ``limit`` requests per
    ``window_seconds``.  Old entries are reaped periodically to bound
    memory usage.
    """

    def __init__(self, limit: int, window_seconds: float) -> None:
        self.limit = limit
        self.window = window_seconds
        self._hits: list[tuple[str, float]] = []
        self._last_reap = time.monotonic()

    def _reap(self) -> None:
        now = time.monotonic()
        if now - self._last_reap > self.window:
            cutoff = now - self.window
            self._hits = [(k, t) for k, t in self._hits if t > cutoff]
            self._last_reap = now

    def is_limited(self, key: str) -> bool:
        """Return ``True`` if *key* has exceeded the limit."""
        self._reap()
        now = time.monotonic()
        cutoff = now - self.window
        recent = sum(1 for k, t in self._hits if k == key and t > cutoff)
        if recent <= self.limit:
            self._hits.append((key, now))
            return False
        return True


def _parse_rate_limit(rate: str) -> tuple[int, float]:
    """Parse a rate limit string like ``'30/minute'`` into (count, seconds)."""
    parts = rate.strip().split("/", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid rate format: {rate!r}")
    count = int(parts[0])
    unit = parts[1].lower()
    seconds = {
        "second": 1, "seconds": 1,
        "minute": 60, "minutes": 60,
        "hour": 3600, "hours": 3600,
    }.get(unit)
    if seconds is None:
        raise ValueError(f"Unknown rate unit: {unit!r}")
    return count, seconds


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Load the emotion model once at startup, release on shutdown."""
    settings: Settings = get_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    models = EmotionModelService(settings)
    models.load()

    explainer = ExplanationService(models, settings)
    service = AnalysisService(models, explainer, settings)

    routes._settings = settings
    routes._model_service = models
    routes._analysis_service = service
    logger.info("Sentimenta API ready (%s)", settings.version)

    yield

    routes._settings = None
    routes._model_service = None
    routes._analysis_service = None
    logger.info("Shutting down")


async def add_security_headers(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Attach conservative security headers to every response."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    return response


async def add_rate_limiting(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Apply per-IP rate limiting to every request."""
    limiter: _RateLimiter | None = getattr(
        request.app.state, "limiter", None
    )
    if limiter is not None:
        client_ip = request.client.host if request.client else "unknown"
        if limiter.is_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "rate_limited",
                        "message": "Too many requests. Please try again later.",
                    }
                },
            )
    return await call_next(request)  # type: ignore[no-any-return]


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    # --- rate limiter ---
    limiter: _RateLimiter | None = None
    try:
        count, seconds = _parse_rate_limit(settings.rate_limit)
        limiter = _RateLimiter(count, seconds)
        logger.info("Rate limit enabled: %s", settings.rate_limit)
    except ValueError:
        logger.warning(
            "Invalid SENTIMENTA_RATE_LIMIT %r — rate limiting disabled",
            settings.rate_limit,
        )

    # --- application ---
    docs_url = "/docs" if settings.enable_docs else None
    redoc_url = "/redoc" if settings.enable_docs else None
    openapi_url = "/openapi.json" if settings.enable_docs else None
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )
    app.state.limiter = limiter

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    app.add_middleware(BaseHTTPMiddleware, dispatch=add_security_headers)
    app.add_middleware(BaseHTTPMiddleware, dispatch=add_rate_limiting)
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        RequestValidationError, validation_error_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, unhandled_error_handler)  # type: ignore[arg-type]
    app.include_router(routes.router)
    return app


app = create_app()
