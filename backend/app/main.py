# backend/app/main.py
# FastAPI application factory and startup lifespan that loads the
# emotion model exactly once before accepting requests.

import logging
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Load the emotion model once at startup, release on shutdown."""
    settings: Settings = get_settings()
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
    response.headers.setdefault(
        "Cross-Origin-Resource-Policy", "same-origin"
    )
    return response


def create_app() -> FastAPI:
    """Build and configure the FastAPI application.

    Returns:
        A fully configured application with CORS, security headers,
        error handlers, and the analysis endpoints mounted under
        ``/api``.
    """
    settings = get_settings()
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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(BaseHTTPMiddleware, dispatch=add_security_headers)
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        RequestValidationError, validation_error_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, unhandled_error_handler)  # type: ignore[arg-type]
    app.include_router(routes.router)
    return app


app = create_app()
