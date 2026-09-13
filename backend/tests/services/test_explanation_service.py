# backend/tests/services/test_explanation_service.py
# Explanation generation: probability fallbacks, summary wording, and
# word/phrase aggregation from token attributions.

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.core.emotions import Emotion
from app.services.explanation_service import ExplanationService


class FakeModelService:
    def __init__(self, loaded: bool = True) -> None:
        self.is_loaded = loaded


def _settings(**overrides: object) -> Settings:
    defaults: dict[str, object] = dict(
        model_id="test-model",
        emotion_threshold=0.30,
        enable_attribution=False,
        device="cpu",
    )
    defaults.update(overrides)
    return Settings(**defaults)  # type: ignore[arg-type]


def _scores(joy: float = 0.80, anger: float = 0.40) -> dict[Emotion, float]:
    scores = {e: 0.01 for e in Emotion}
    scores.update(
        {Emotion.JOY: joy, Emotion.ANGER: anger, Emotion.NEUTRAL: 0.05}
    )
    return scores


def test_probability_fallback_when_attribution_disabled() -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(), _settings(enable_attribution=False)
    )
    explanation = service.explain("hello", _scores())
    assert explanation.method == "probabilities"
    assert explanation.signals == []
    assert explanation.target_label is Emotion.JOY
    assert "joy" in explanation.summary
    assert "Token-level evidence is unavailable" in explanation.summary


def test_probability_fallback_when_model_not_loaded() -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(loaded=False), _settings(enable_attribution=True)
    )
    explanation = service.explain("hello", _scores())
    assert explanation.method == "probabilities"


def test_attribution_failure_falls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(), _settings(enable_attribution=True)
    )

    def boom(text: str, target: Emotion) -> list:
        raise RuntimeError("attribution exploded")

    monkeypatch.setattr(service, "_attribute", boom)
    explanation = service.explain("hello", _scores())
    assert explanation.method == "probabilities"
    assert explanation.signals == []


def test_attribution_success_mentions_highlights(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(), _settings(enable_attribution=True)
    )
    monkeypatch.setattr(service, "_attribute", lambda text, target: [])
    explanation = service.explain("hello", _scores())
    assert explanation.method == "integrated_gradients"
    assert "highlighted words" in explanation.summary


def test_summary_lists_secondary_emotions() -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(), _settings(enable_attribution=False)
    )
    explanation = service.explain("hello", _scores(joy=0.80, anger=0.40))
    assert "anger" in explanation.summary


def test_summary_percentage_rounds() -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(), _settings(enable_attribution=False)
    )
    explanation = service.explain("hello", _scores(joy=0.876, anger=0.01))
    assert "88% confidence" in explanation.summary


def test_words_to_signals_merges_adjacent_words() -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(), _settings()
    )
    signals = service._words_to_signals(
        "I love cake", [[0, 1], [2, 6], [7, 11]], [0.05, 0.9, 0.2]
    )
    assert len(signals) == 1
    assert signals[0].text == "love cake"
    assert signals[0].weight == pytest.approx(1.0)


def test_words_to_signals_empty_when_no_positive() -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(), _settings()
    )
    signals = service._words_to_signals(
        "abc", [[0, 1], [1, 2], [2, 3]], [-0.1, -0.2, -0.3]
    )
    assert signals == []


def test_words_to_signals_cutoff_removes_weak_words() -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(), _settings()
    )
    signals = service._words_to_signals(
        "strong weak", [[0, 6], [7, 11]], [1.0, 0.01]
    )
    assert len(signals) == 1
    assert signals[0].text == "strong"


def test_words_to_signals_ignores_zero_length_offsets() -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(), _settings()
    )
    signals = service._words_to_signals(
        "hi", [[0, 0], [0, 2], [2, 2]], [0.0, 0.9, 0.0]
    )
    assert len(signals) == 1
    assert signals[0].text == "hi"


def test_words_to_signals_returns_at_most_three_phrases() -> None:
    service = ExplanationService(  # type: ignore[arg-type]
        FakeModelService(), _settings()
    )
    text = "a b c d e f g"
    offsets = [[i * 2, i * 2 + 1] for i in range(7)]
    attrs = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
    signals = service._words_to_signals(text, offsets, attrs)
    assert len(signals) <= 3
