# backend/app/main.py
# FastAPI application factory and startup lifespan that loads the
# emotion model exactly once before accepting requests.

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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


def create_app() -> FastAPI:
    """Build and configure the FastAPI application.

    Returns:
        A fully configured application with CORS, error handlers,
        and the analysis endpoints mounted under ``/api``.
    """
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        RequestValidationError, validation_error_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, unhandled_error_handler)  # type: ignore[arg-type]
    app.include_router(routes.router)
    return app


app = create_app()
