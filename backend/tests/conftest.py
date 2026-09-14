# backend/tests/conftest.py
# Shared fixtures: fake settings, stub model/explanation services,
# and a test client wired to the dependency-injection overrides.

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.emotions import Emotion, EmotionGroup
from app.schemas.analysis import (
    AnalyzeResponse,
    EmotionScore,
    Explanation,
    Intensity,
    Profile,
)
from app.api import routes
from app.services.analysis_service import AnalysisService


def _make_settings(**overrides: object) -> Settings:
    """Return a Settings instance with sensible test defaults."""
    defaults = dict(
        model_id="test-model",
        cors_origins=["http://localhost:5173"],
        max_text_chars=2000,
        emotion_threshold=0.30,
        enable_attribution=False,
        device="cpu",
        rate_limit="0",  # disable rate limiting in tests
    )
    defaults.update(overrides)  # type: ignore[arg-type]
    return Settings(**defaults)


class StubAnalysisService(AnalysisService):
    """Deterministic stand-in that never touches PyTorch.

    Every call to ``analyze`` or ``analyze_sentences`` returns a
    fixed profile built from ``_STUB_SCORES``.
    """

    _STUB_SCORES: dict[Emotion, float] = {
        Emotion.JOY: 0.85,
        Emotion.EXCITEMENT: 0.70,
        Emotion.OPTIMISM: 0.45,
        Emotion.NERVOUSNESS: 0.25,
        Emotion.NEUTRAL: 0.10,
        **{e: 0.02 for e in Emotion if e not in {
            Emotion.JOY, Emotion.EXCITEMENT, Emotion.OPTIMISM,
            Emotion.NERVOUSNESS, Emotion.NEUTRAL,
        }},
    }

    def __init__(self) -> None:
        self._settings = _make_settings()
        super().__init__(
            model_service=None,  # type: ignore[arg-type]
            explanation_service=None,  # type: ignore[arg-type]
            settings=self._settings,
        )

    def analyze(self, text: str, include_sentences: bool = False):  # type: ignore[override]
        scores = self._STUB_SCORES
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        detected = [(e, s) for e, s in ranked if s >= self._settings.emotion_threshold]
        return AnalyzeResponse(
            primary_emotion=EmotionScore(
                label=ranked[0][0], score=round(ranked[0][1], 4)
            ),
            emotions=[
                EmotionScore(label=e, score=round(s, 4))
                for e, s in detected
            ],
            all_emotions=[
                EmotionScore(label=e, score=round(s, 4))
                for e, s in ranked
            ],
            intensity=Intensity(score=0.90, label="high"),
            profile=Profile(
                positive=5.0, negative=1.0, cognitive=0.5, neutral=0.1,
                shares={g: 0.25 for g in EmotionGroup},
            ),
            explanation=Explanation(
                summary="Stub explanation.",
                signals=[],
                method="probabilities",
                target_label=Emotion.JOY,
            ),
            sentences=[],
            metadata={
                "model_id": "test-model",
                "char_count": len(text),
                "word_count": len(text.split()),
                "sentence_count": 1,
                "threshold": self._settings.emotion_threshold,
                "attribution_used": False,
                "truncated_tokens": False,
                "latency_ms": {"inference": 5.0, "explanation": 2.0, "total": 7.0},
            },
        )

    def analyze_sentences(self, text: str):  # type: ignore[override]
        from app.schemas.analysis import SentenceAnalysis, SentenceAnalysisResponse
        sentences = [
            SentenceAnalysis(
                index=0,
                text=text,
                primary_emotion=EmotionScore(label=Emotion.JOY, score=0.85),
                emotions=[],
            )
        ]
        return SentenceAnalysisResponse(
            sentences=sentences,
            metadata={
                "model_id": "test-model",
                "char_count": len(text),
                "word_count": len(text.split()),
                "sentence_count": 1,
                "threshold": self._settings.emotion_threshold,
                "attribution_used": False,
                "truncated_tokens": False,
                "latency_ms": {"inference": 3.0, "explanation": 0.0, "total": 3.0},
            },
        )


@pytest.fixture
def stub_service() -> StubAnalysisService:
    return StubAnalysisService()


@pytest.fixture
def app(stub_service: StubAnalysisService):  # type: ignore[no-untyped-def]
    """A fresh FastAPI app with all service dependencies stubbed."""
    from app.main import create_app
    settings = _make_settings()
    application = create_app()
    application.dependency_overrides[routes.get_analysis_service] = lambda: stub_service
    application.dependency_overrides[routes.get_settings] = lambda: settings
    application.dependency_overrides[routes.get_model_service] = lambda: _StubModelService(settings)
    return application


@pytest.fixture
async def client(app) -> AsyncClient:  # type: ignore[no-untyped-def]
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class _StubModelService:
    """Bare stand-in for EmotionModelService with is_loaded=True."""
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.is_loaded = True
