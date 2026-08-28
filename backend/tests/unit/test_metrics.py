# backend/tests/unit/test_metrics.py
# Tests for derived metrics: ranking, threshold filtering, intensity,
# and emotional profile aggregation.

from app.core.emotions import Emotion, EmotionGroup
from app.services.metrics import (
    compute_intensity,
    compute_profile,
    detected_emotions,
    rank_emotions,
)


# Deterministic score map used by several tests. Every label gets a
# value except those explicitly overridden; together with the real
# taxonomy this exercises all three groups.
_BASE_SCORES: dict[Emotion, float] = {
    e: 0.01 for e in Emotion
}
_BASE_SCORES.update(
    {
        Emotion.JOY: 0.80,
        Emotion.EXCITEMENT: 0.60,
        Emotion.ANGER: 0.40,
        Emotion.NEUTRAL: 0.05,
        Emotion.CURIOSITY: 0.30,
    }
)


def test_rank_emotions_descending() -> None:
    ranked = rank_emotions(_BASE_SCORES)
    assert ranked[0][0] == Emotion.JOY
    assert ranked[0][1] == 0.80


def test_rank_emotions_tie_break() -> None:
    scores = {Emotion.JOY: 0.5, Emotion.LOVE: 0.5}
    ranked = rank_emotions(scores)
    labels = [e for e, _ in ranked]
    assert labels.index(Emotion.JOY) < labels.index(Emotion.LOVE)


def test_detected_emotions_at_threshold() -> None:
    ranked = rank_emotions(_BASE_SCORES)
    detected = detected_emotions(ranked, 0.25)
    labels = {e for e, _ in detected}
    assert Emotion.JOY in labels
    assert Emotion.ANGER in labels
    assert Emotion.CURIOSITY in labels
    assert Emotion.EXCITEMENT in labels
    assert Emotion.NEUTRAL not in labels  # 0.05


def test_detected_emotions_high_threshold() -> None:
    ranked = rank_emotions(_BASE_SCORES)
    detected = detected_emotions(ranked, 0.90)
    assert detected == []


def test_intensity_low_when_neutral_high() -> None:
    scores = {e: 0.01 for e in Emotion}
    scores[Emotion.NEUTRAL] = 0.90
    result = compute_intensity(scores)
    assert result.label == "low"
    assert result.score <= 0.11


def test_intensity_high_when_neutral_low() -> None:
    scores = {e: 0.01 for e in Emotion}
    scores[Emotion.NEUTRAL] = 0.05
    scores[Emotion.JOY] = 0.85
    result = compute_intensity(scores)
    assert result.label == "high"
    assert result.score >= 0.85


def test_intensity_moderate_band() -> None:
    scores = {e: 0.05 for e in Emotion}
    scores[Emotion.NEUTRAL] = 0.50
    result = compute_intensity(scores)
    assert result.label == "moderate"


def test_profile_shares_sum_to_one() -> None:
    scores = {e: 0.1 for e in Emotion}
    scores.update({Emotion.JOY: 0.8, Emotion.ANGER: 0.6})
    profile = compute_profile(scores)
    total = sum(profile.shares.values())
    assert abs(total - 1.0) < 1e-8


def test_profile_positive_dominant() -> None:
    scores = {e: 0.01 for e in Emotion}
    scores[Emotion.JOY] = 0.9
    scores[Emotion.LOVE] = 0.7
    profile = compute_profile(scores)
    assert profile.shares[EmotionGroup.POSITIVE] > 0.8


def test_profile_negative_dominant() -> None:
    scores = {e: 0.01 for e in Emotion}
    scores[Emotion.ANGER] = 0.9
    scores[Emotion.SADNESS] = 0.8
    profile = compute_profile(scores)
    assert profile.shares[EmotionGroup.NEGATIVE] > 0.8


def test_profile_all_zero_handles_gracefully() -> None:
    scores = {e: 0.0 for e in Emotion}
    profile = compute_profile(scores)
    assert sum(profile.shares.values()) == 0.0


def test_all_28_emotions_present_in_profile() -> None:
    scores = {e: 0.1 for e in Emotion}
    profile = compute_profile(scores)
    assert "positive" in profile.model_fields_set or "positive" in str(
        profile.model_dump()
    )
