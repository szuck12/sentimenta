# backend/app/api/routes.py
# REST endpoints: health, taxonomy, single-text analysis, and
# sentence-level analysis.

from fastapi import APIRouter, Depends

from ..core.config import Settings
from ..schemas.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    EmotionInfo,
    EmotionsResponse,
    HealthResponse,
    SentenceAnalysisRequest,
    SentenceAnalysisResponse,
)
from ..core.emotions import (
    EMOJIS,
    DESCRIPTIONS,
    Emotion,
    GROUP_LABELS,
    group_of,
)
from ..services.analysis_service import AnalysisService
from ..services.emotion_model_service import EmotionModelService

router = APIRouter(prefix="/api")


def get_settings() -> Settings:
    """FastAPI dependency returning the cached settings."""
    if _settings is None:
        raise RuntimeError("Settings not initialised")
    return _settings


def get_analysis_service() -> AnalysisService:
    """FastAPI dependency returning the app-level analysis service."""
    if _analysis_service is None:
        raise RuntimeError("AnalysisService not initialised")
    return _analysis_service


def get_model_service() -> EmotionModelService:
    """FastAPI dependency returning the app-level model service."""
    if _model_service is None:
        raise RuntimeError("ModelService not initialised")
    return _model_service


# Populated by create_app(); module-level singletons keep the
# dependency functions signature-simple for tests to override.
_settings: Settings | None = None
_analysis_service: AnalysisService | None = None
_model_service: EmotionModelService | None = None


@router.get("/health", response_model=HealthResponse)
def health(
    models: EmotionModelService = Depends(get_model_service),
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Report service liveness and whether the model is ready."""
    return HealthResponse(
        status="ok",
        version=settings.version,
        model_loaded=models.is_loaded,
    )


@router.get("/emotions", response_model=EmotionsResponse)
def emotions(settings: Settings = Depends(get_settings)) -> EmotionsResponse:
    """Return the full GoEmotions taxonomy with Sentimenta metadata."""
    infos = [
        EmotionInfo(
            label=emotion,
            emoji=EMOJIS[emotion],
            group=group_of(emotion),
            description=DESCRIPTIONS[emotion],
        )
        for emotion in Emotion
    ]
    return EmotionsResponse(
        count=len(infos),
        groups={g.value: label for g, label in GROUP_LABELS.items()},
        emotions=infos,
    )


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    request: AnalyzeRequest,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalyzeResponse:
    """Analyze one block of text and explain the reading.

    The primary emotion, all detected secondary emotions, derived
    intensity/profile metrics, an evidence-based explanation, and —
    optionally — per-sentence analyses are returned.
    """
    return service.analyze(
        request.text, include_sentences=request.include_sentences
    )


@router.post(
    "/analyze/sentences", response_model=SentenceAnalysisResponse
)
def analyze_sentences(
    request: SentenceAnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service),
) -> SentenceAnalysisResponse:
    """Analyze each sentence of the input independently."""
    return service.analyze_sentences(request.text)
