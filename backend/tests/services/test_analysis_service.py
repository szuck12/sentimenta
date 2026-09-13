# backend/tests/services/test_analysis_service.py
# Orchestration tests for AnalysisService using a PyTorch-free fake
# model service and the real (probability-only) ExplanationService.

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.core.emotions import Emotion
from app.core.errors import EmptyTextError, ModelUnavailableError
from app.services.analysis_service import AnalysisService
from app.services.explanation_service import ExplanationService


def _scores(**overrides: float) -> dict[Emotion, float]:
    scores = {e: 0.01 for e in Emotion}
    scores.update(
        {Emotion.JOY: 0.80, Emotion.EXCITEMENT: 0.60, Emotion.NEUTRAL: 0.05}
    )
    scores.update(overrides)
    return scores


class FakeModelService:
    """Minimal stand-in that records calls and returns fixed scores."""

    def __init__(
        self,
        scores: dict[Emotion, float] | None = None,
        loaded: bool = True,
        truncate_at: int | None = None,
    ) -> None:
        self.is_loaded = loaded
        self._scores = scores or _scores()
        self._truncate_at = truncate_at
        self.calls: list[list[str]] = []

    def predict(self, texts: list[str]) -> list[dict[Emotion, float]]:
        self.calls.append(list(texts))
        return [dict(self._scores) for _ in texts]

    def exceeds_token_budget(self, text: str) -> bool:
        return self._truncate_at is not None and len(text) > self._truncate_at


def _make(
    *,
    settings: Settings | None = None,
    model: FakeModelService | None = None,
    enable_attribution: bool = False,
) -> tuple[AnalysisService, FakeModelService]:
    settings = settings or Settings(
        model_id="test-model",
        emotion_threshold=0.30,
        sentence_limit=10,
        enable_attribution=enable_attribution,
        device="cpu",
    )
    model = model or FakeModelService()
    explainer = ExplanationService(model, settings)  # type: ignore[arg-type]
    return AnalysisService(model, explainer, settings), model  # type: ignore[arg-type]


def test_analyze_returns_primary_and_ranked_emotions() -> None:
    service, _ = _make()
    response = service.analyze("I love this!", include_sentences=False)
    assert response.primary_emotion.label is Emotion.JOY
    assert len(response.all_emotions) == 28
    scores = [e.score for e in response.all_emotions]
    assert scores == sorted(scores, reverse=True)


def test_analyze_filters_detected_by_threshold() -> None:
    service, _ = _make()
    response = service.analyze("I love this!", include_sentences=False)
    labels = {e.label for e in response.emotions}
    assert Emotion.JOY in labels
    assert Emotion.EXCITEMENT in labels
    assert Emotion.NEUTRAL not in labels  # 0.05 < 0.30


def test_analyze_empty_text_raises() -> None:
    service, _ = _make()
    with pytest.raises(EmptyTextError):
        service.analyze("   \n ", include_sentences=False)


def test_analyze_requires_loaded_model() -> None:
    service, _ = _make(model=FakeModelService(loaded=False))
    with pytest.raises(ModelUnavailableError):
        service.analyze("hello", include_sentences=False)


def test_analyze_metadata_counts_and_latency() -> None:
    service, _ = _make()
    response = service.analyze("hello world foo", include_sentences=False)
    assert response.metadata.char_count == len("hello world foo")
    assert response.metadata.word_count == 3
    assert response.metadata.sentence_count == 1
    assert set(response.metadata.latency_ms) == {
        "inference",
        "explanation",
        "total",
    }


def test_analyze_flags_truncation() -> None:
    service, _ = _make(model=FakeModelService(truncate_at=5))
    response = service.analyze("this is definitely too long", include_sentences=False)
    assert response.metadata.truncated_tokens is True


def test_analyze_sentences_respects_limit() -> None:
    settings = Settings(
        model_id="test-model",
        emotion_threshold=0.30,
        sentence_limit=2,
        enable_attribution=False,
        device="cpu",
    )
    service, _ = _make(settings=settings)
    response = service.analyze(
        "One. Two. Three. Four.", include_sentences=True
    )
    assert len(response.sentences) == 2
    assert [s.index for s in response.sentences] == [0, 1]


def test_analyze_without_sentences_returns_empty_list() -> None:
    service, _ = _make()
    response = service.analyze("One. Two.", include_sentences=False)
    assert response.sentences == []


def test_analyze_sentences_endpoint_response() -> None:
    service, _ = _make()
    response = service.analyze_sentences("First. Second.")
    assert [s.text for s in response.sentences] == ["First.", "Second."]
    assert response.metadata.attribution_used is False


def test_probability_method_sets_attribution_false() -> None:
    service, _ = _make(enable_attribution=False)
    response = service.analyze("hello", include_sentences=False)
    assert response.explanation.method == "probabilities"
    assert response.metadata.attribution_used is False


def test_integrated_gradients_sets_attribution_true(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, _ = _make(enable_attribution=True)

    def fake_attribute(text: str, target: Emotion) -> list:
        return []

    monkeypatch.setattr(service.explainer, "_attribute", fake_attribute)
    response = service.analyze("hello", include_sentences=False)
    assert response.explanation.method == "integrated_gradients"
    assert response.metadata.attribution_used is True
