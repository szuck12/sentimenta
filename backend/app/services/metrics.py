# backend/app/services/metrics.py
# Derived metrics computed from raw model probabilities: threshold
# filtering, ranking, emotional intensity, and the grouped profile.

from ..core.emotions import Emotion, EmotionGroup, GROUP_MEMBERS
from ..schemas.analysis import Intensity, Profile

# Score bands for the derived intensity metric. Chosen so that a text
# dominated by neutral (P >= 0.65) reads as "low" and strongly
# signalled text (neutral <= 0.35) reads as "high".
_INTENSITY_BANDS: tuple[tuple[float, str], ...] = (
    (0.35, "low"),
    (0.65, "moderate"),
)


def rank_emotions(
    scores: dict[Emotion, float],
) -> list[tuple[Emotion, float]]:
    """Sort all 28 emotion scores from highest to lowest.

    Args:
        scores: Mapping of every GoEmotions label to its probability.

    Returns:
        (emotion, score) pairs sorted descending by score; ties break
        alphabetically by label for deterministic output.
    """
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def detected_emotions(
    ranked: list[tuple[Emotion, float]], threshold: float
) -> list[tuple[Emotion, float]]:
    """Filter ranked emotions down to those at or above a threshold.

    Args:
        ranked: Output of :func:`rank_emotions`.
        threshold: Minimum probability to count as "detected".

    Returns:
        The filtered prefix of ``ranked`` (order preserved).
    """
    return [(e, s) for e, s in ranked if s >= threshold]


def compute_intensity(scores: dict[Emotion, float]) -> Intensity:
    """Derive the Sentimenta emotional-intensity metric.

    Defined as ``1 - P(neutral)``: emotionally flat text scores near
    zero, strongly signalled text approaches one. This is a
    Sentimenta-derived presentation metric — GoEmotions does not
    predict "intensity".

    Args:
        scores: Mapping of all labels to probabilities; must contain
            the neutral label.

    Returns:
        Intensity with both the numeric score and its band label.
    """
    score = max(0.0, min(1.0, 1.0 - scores.get(Emotion.NEUTRAL, 0.0)))
    label = "high"
    for upper, band in _INTENSITY_BANDS:
        if score < upper:
            label = band
            break
    return Intensity(score=round(score, 4), label=label)


def compute_profile(scores: dict[Emotion, float]) -> Profile:
    """Aggregate raw scores into Sentimenta's four profile groups.

    Each group's value is the sum of its member emotions' sigmoid
    probabilities (multi-label outputs do not sum to one, so sums can
    exceed 1). Shares normalise the four group sums to total 1 so the
    frontend can render them as parts-of-a-whole.

    Args:
        scores: Mapping of all 28 labels to probabilities.

    Returns:
        A Profile with per-group sums plus normalised shares.
    """
    totals: dict[EmotionGroup, float] = {}
    for group in EmotionGroup:
        totals[group] = round(
            sum(scores.get(e, 0.0) for e in GROUP_MEMBERS[group]), 4
        )
    grand = sum(totals.values())
    shares = {
        group: (totals[group] / grand if grand > 0 else 0.0)
        for group in EmotionGroup
    }
    return Profile(
        positive=totals[EmotionGroup.POSITIVE],
        negative=totals[EmotionGroup.NEGATIVE],
        cognitive=totals[EmotionGroup.COGNITIVE],
        neutral=totals[EmotionGroup.NEUTRAL],
        shares=shares,
    )
