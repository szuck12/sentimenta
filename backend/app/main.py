# backend/app/main.py
# FastAPI application factory and startup lifespan that loads the
# emotion model exactly once before accepting requests.

import asyncio
import logging
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
from .core.ratelimit import RateLimiter, client_ip, parse_rate_limit
from .services.analysis_service import AnalysisService
from .services.emotion_model_service import EmotionModelService
from .services.explanation_service import ExplanationService

logger = logging.getLogger(__name__)

# Only these paths are subject to the concurrency cap (the expensive,
# model-backed analysis endpoints).
_CONCURRENCY_PREFIX = "/api/analyze"


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Build a standard error envelope response."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


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


async def enforce_body_size(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Reject requests whose declared body exceeds the configured limit."""
    limit: int = getattr(request.app.state, "max_body_bytes", 0)
    if limit:
        header = request.headers.get("content-length")
        if header is not None:
            try:
                length = int(header)
            except ValueError:
                return _error_response(
                    400,
                    "invalid_content_length",
                    "The Content-Length header is invalid.",
                )
            if length > limit:
                return _error_response(
                    413,
                    "request_too_large",
                    "The request body is too large.",
                )
    return await call_next(request)  # type: ignore[no-any-return]


async def limit_concurrency(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Cap the number of concurrent analysis requests."""
    semaphore: asyncio.Semaphore | None = getattr(
        request.app.state, "concurrency_sem", None
    )
    if semaphore is None or not request.url.path.startswith(
        _CONCURRENCY_PREFIX
    ):
        return await call_next(request)  # type: ignore[no-any-return]
    wait = getattr(request.app.state, "max_queue_wait_seconds", 5.0)
    try:
        await asyncio.wait_for(semaphore.acquire(), timeout=wait)
    except asyncio.TimeoutError:
        return _error_response(
            503,
            "server_busy",
            "The analysis service is busy. Please try again shortly.",
        )
    try:
        return await call_next(request)  # type: ignore[no-any-return]
    finally:
        semaphore.release()


async def enforce_rate_limit(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Apply per-client rate limiting to every request."""
    limiter: RateLimiter | None = getattr(
        request.app.state, "limiter", None
    )
    if limiter is not None:
        trust_proxy: bool = getattr(request.app.state, "trust_proxy", False)
        if limiter.is_limited(client_ip(request, trust_proxy)):
            return _error_response(
                429,
                "rate_limited",
                "Too many requests. Please try again later.",
            )
    return await call_next(request)  # type: ignore[no-any-return]


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    # --- rate limiter ---
    limiter: RateLimiter | None = None
    try:
        parsed = parse_rate_limit(settings.rate_limit)
        if parsed is not None:
            count, seconds = parsed
            limiter = RateLimiter(count, seconds)
            logger.info("Rate limit enabled: %s", settings.rate_limit)
        else:
            logger.info("Rate limiting disabled")
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
    app.state.trust_proxy = settings.trust_proxy
    app.state.max_body_bytes = settings.max_body_bytes
    app.state.max_queue_wait_seconds = settings.max_queue_wait_seconds
    app.state.concurrency_sem = (
        asyncio.Semaphore(settings.max_concurrent_requests)
        if settings.max_concurrent_requests > 0
        else None
    )

    # Middleware are applied innermost-first: the last one added is the
    # outermost.  We want CORS and the security headers to wrap every
    # response (including 413/429/503), so they are added last.
    app.add_middleware(BaseHTTPMiddleware, dispatch=enforce_rate_limit)
    app.add_middleware(BaseHTTPMiddleware, dispatch=limit_concurrency)
    app.add_middleware(BaseHTTPMiddleware, dispatch=enforce_body_size)
    app.add_middleware(BaseHTTPMiddleware, dispatch=add_security_headers)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        RequestValidationError, validation_error_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, unhandled_error_handler)  # type: ignore[arg-type]
    app.include_router(routes.router)
    return app


app = create_app()
