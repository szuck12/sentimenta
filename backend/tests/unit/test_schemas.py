# backend/tests/unit/test_schemas.py
# Pydantic request/response constraints that define the API contract.

import pytest
from pydantic import ValidationError

from app.core.emotions import Emotion, EmotionGroup
from app.schemas.analysis import (
    AnalyzeRequest,
    EmotionScore,
    EvidenceSignal,
    Explanation,
    Profile,
    SentenceAnalysisRequest,
)


def test_analyze_request_defaults() -> None:
    request = AnalyzeRequest(text="hello")
    assert request.include_sentences is False


@pytest.mark.parametrize("text", ["", "x" * 2001])
def test_analyze_request_length_bounds(text: str) -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(text=text)


@pytest.mark.parametrize("text", ["", "x" * 2001])
def test_sentence_request_length_bounds(text: str) -> None:
    with pytest.raises(ValidationError):
        SentenceAnalysisRequest(text=text)


@pytest.mark.parametrize("score", [-0.01, 1.01])
def test_emotion_score_must_be_probability(score: float) -> None:
    with pytest.raises(ValidationError):
        EmotionScore(label=Emotion.JOY, score=score)


def test_emotion_score_accepts_bounds() -> None:
    assert EmotionScore(label=Emotion.JOY, score=0.0).score == 0.0
    assert EmotionScore(label=Emotion.JOY, score=1.0).score == 1.0


@pytest.mark.parametrize("weight", [-1.0, 0.0, 1.0])
def test_evidence_signal_accepts_attribution_range(weight: float) -> None:
    assert EvidenceSignal(text="word", weight=weight).weight == weight


@pytest.mark.parametrize("weight", [-1.01, 1.01])
def test_evidence_signal_rejects_out_of_range(weight: float) -> None:
    with pytest.raises(ValidationError):
        EvidenceSignal(text="word", weight=weight)


def test_explanation_defaults_to_no_signals() -> None:
    explanation = Explanation(
        summary="s", method="probabilities", target_label=Emotion.JOY,
        target_percentage=50,
    )
    assert explanation.signals == []


def test_profile_shares_use_emotion_groups() -> None:
    profile = Profile(
        positive=1.0,
        negative=0.5,
        cognitive=0.25,
        neutral=0.25,
        shares={group: 0.25 for group in EmotionGroup},
    )
    assert set(profile.shares) == set(EmotionGroup)
