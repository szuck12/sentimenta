# backend/app/services/explanation_service.py
# Evidence-based explanations: Captum integrated-gradients token
# attribution mapped back to words/phrases, plus factual,
# template-generated summaries built strictly from model outputs.

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import torch

from ..core.config import Settings
from ..core.emotions import Emotion
from ..schemas.analysis import EvidenceSignal, Explanation
from .emotion_model_service import EmotionModelService

logger = logging.getLogger(__name__)

# Words whose positive attribution falls below this fraction of the
# strongest word are not treated as evidence.
_SIGNAL_CUTOFF_RATIO = 0.15

# Human-readable labels for each emotion, used in the summary narrative.
_EMOTION_DESCRIPTIONS: dict[str, str] = {
    "admiration": "admiration for something impressive",
    "amusement": "amusement or entertainment",
    "anger": "strong displeasure or frustration",
    "annoyance": "irritation or being bothered",
    "approval": "agreement with or endorsement of something",
    "caring": "warmth, concern, or compassion",
    "confusion": "uncertainty or lack of clarity",
    "curiosity": "a desire to learn or know more",
    "desire": "wanting or longing for something",
    "disappointment": "let-down from unmet expectations",
    "disapproval": "objection or disagreement",
    "disgust": "repulsion or being put off",
    "embarrassment": "awkwardness or self-consciousness",
    "excitement": "enthusiasm and eager anticipation",
    "fear": "apprehension or worry about something threatening",
    "gratitude": "thankfulness and appreciation",
    "grief": "deep sorrow, often from loss",
    "joy": "happiness and delight",
    "love": "deep affection and attachment",
    "nervousness": "anxiety or unease about what may happen",
    "optimism": "hopefulness that things will work out well",
    "pride": "satisfaction in achievements or qualities",
    "realization": "a moment of sudden understanding",
    "relief": "ease after a worry or difficulty has passed",
    "remorse": "regret or guilt about something done",
    "sadness": "unhappiness or sorrow",
    "surprise": "being startled by the unexpected",
    "neutral": "no strong emotional signal",
}


def _score_to_percentage(scores: dict[Emotion, float]) -> dict[Emotion, int]:
    """Convert model scores to whole-number percentages summing to 100.

    Uses the largest-remainder (Hamilton) method: every score is
    scaled to its share of the total, floored, and the leftover
    points are handed to the emotions with the largest fractional
    parts.  The result is deterministic and mirrors the algorithm
    used by the frontend's ``toWholePercentages``.
    """
    sorted_emotions = sorted(scores.keys(), key=lambda e: e.value)
    values = [scores[e] for e in sorted_emotions]
    total = sum(values)
    if total <= 0:
        return {e: 0 for e in scores}
    exact = [(v / total) * 100 for v in values]
    result = [int(v) for v in exact]
    used = sum(result)
    remainder = 100 - used
    order = sorted(
        range(len(exact)),
        key=lambda i: exact[i] - int(exact[i]),
        reverse=True,
    )
    for i in range(remainder):
        result[order[i]] += 1
    return {e: p for e, p in zip(sorted_emotions, result)}


class ExplanationService:
    """Produces explanations grounded in model-derived evidence.

    Two evidence tiers exist:

    1. Token attribution (Captum LayerIntegratedGradients against the
       primary emotion's output neuron), aggregated from subword
       tokens to words to adjacent-word phrases.
    2. Probability-only summaries used when attribution is disabled
       or fails — never fabricated token evidence.
    """

    def __init__(
        self, model_service: EmotionModelService, settings: Settings
    ) -> None:
        self.models = model_service
        self.settings = settings

    def explain(self, text: str, prediction_scores: dict[Emotion, float]) -> Explanation:
        """Explain why ``prediction_scores`` favor a primary emotion.

        Args:
            text: The analyzed input text.
            prediction_scores: Full 28-label probability mapping from
                the primary inference pass.

        Returns:
            An Explanation with the target label, its normalized
            percentage (matching the Emotion Mix / Full Spectrum), a
            factual summary, and (when available) attributed key-signal
            phrases.
        """
        ranked = sorted(
            prediction_scores.items(), key=lambda kv: (-kv[1], kv[0])
        )
        target, _target_score = ranked[0]

        # Derive the same whole-number percentages the frontend uses.
        pct_map = _score_to_percentage(prediction_scores)
        target_pct = pct_map[target]
        others_pct: list[tuple[Emotion, int]] = [
            (emotion, pct_map[emotion])
            for emotion, _score in ranked[1:]
            if pct_map[emotion] >= 10
        ][:2]

        if not self.settings.enable_attribution or not self.models.is_loaded:
            return self._probability_explanation(
                target, target_pct, others_pct
            )

        try:
            signals = self._attribute(text, target)
        except Exception as exc:
            logger.warning("Token attribution failed: %s", exc)
            return self._probability_explanation(
                target, target_pct, others_pct
            )

        return Explanation(
            summary=self._summary(target, target_pct, others_pct, True),
            signals=signals,
            method="integrated_gradients",
            target_label=target,
            target_percentage=target_pct,
        )

    def _probability_explanation(
        self,
        target: Emotion,
        target_pct: int,
        others_pct: list[tuple[Emotion, int]],
    ) -> Explanation:
        """Build the fallback explanation from probabilities alone."""
        return Explanation(
            summary=self._summary(target, target_pct, others_pct, False),
            signals=[],
            method="probabilities",
            target_label=target,
            target_percentage=target_pct,
        )

    def _summary(
        self,
        target: Emotion,
        target_pct: int,
        others_pct: list[tuple[Emotion, int]],
        has_signals: bool,
    ) -> str:
        """Render a 1-3 sentence descriptive summary.

        The summary names the primary emotion with its percentage and
        describes the emotional tone of the text.  If other emotions are
        prevalent (≥ 10 % share) they are woven into the narrative to
        paint a fuller picture.

        Args:
            target: Primary emotion label.
            target_pct: Its normalized percentage (0-100).
            others_pct: Secondary emotions with their percentages,
                already sorted descending and filtered ≥ 10 %.
            has_signals: Whether token evidence is included below.

        Returns:
            A concise, factual 1-3 sentence description.
        """
        primary_desc = _EMOTION_DESCRIPTIONS.get(
            target.value, target.value
        )
        primary_clause = (
            f"The text conveys {primary_desc} ({target_pct}%)"
        )

        if not others_pct:
            return f"{primary_clause}."

        if len(others_pct) == 1:
            e, pct = others_pct[0]
            sec_desc = _EMOTION_DESCRIPTIONS.get(e.value, e.value)
            return f"{primary_clause}, along with {sec_desc} ({pct}%)."

        e1, pct1 = others_pct[0]
        e2, pct2 = others_pct[1]
        d1 = _EMOTION_DESCRIPTIONS.get(e1.value, e1.value)
        d2 = _EMOTION_DESCRIPTIONS.get(e2.value, e2.value)
        return f"{primary_clause}, {d1} ({pct1}%), and {d2} ({pct2}%)."

    def _attribute(
        self, text: str, target: Emotion
    ) -> list[EvidenceSignal]:
        """Run integrated gradients and extract key phrases.

        Args:
            text: Input text (short enough for one model pass).
            target: The emotion output neuron to attribute against.

        Returns:
            Up to five phrases with normalized positive weights.  At
            least one phrase is returned whenever the input contains a
            usable word token; the list is empty only when there are no
            word tokens at all.

        Raises:
            RuntimeError: Propagated from the model service when the
                forward passes fail.
        """
        models = self.models
        assert models.model is not None and models.tokenizer is not None

        import torch
        from captum.attr import LayerIntegratedGradients

        prediction = models.predict_with_offsets(text)
        encoding = prediction.encoding
        input_ids = encoding["input_ids"]
        attention_mask = encoding["attention_mask"]

        if input_ids.shape[1] <= 2:
            return []

        pad_id = models.tokenizer.pad_token_id or 1
        baseline_ids = torch.full_like(input_ids, pad_id)

        def forward_func(ids: torch.Tensor) -> torch.Tensor:
            mask = attention_mask.to(ids.device)
            outputs = models.model(
                input_ids=ids, attention_mask=mask
            ).logits
            return torch.sigmoid(outputs)

        label2id: dict[str, int] = models.model.config.label2id
        target_idx = label2id[target.value]

        lig = LayerIntegratedGradients(
            forward_func, models.model.get_input_embeddings()
        )
        attrs = lig.attribute(
            inputs=input_ids.to(models.device),
            baselines=baseline_ids.to(models.device),
            target=target_idx,
            n_steps=self.settings.attribution_steps,
            internal_batch_size=max(
                1, min(8, self.settings.attribution_steps)
            ),
        )
        token_attrs = attrs.sum(dim=-1).squeeze(0).detach().cpu()
        offsets = encoding["offset_mapping"][0].tolist()

        return self._words_to_signals(text, offsets, token_attrs)

    def _words_to_signals(
        self,
        text: str,
        offsets: list[list[int]],
        token_attrs: torch.Tensor,
    ) -> list[EvidenceSignal]:
        """Aggregate subtoken attributions into word-level phrases.

        Args:
            text: Original input text.
            offsets: Per-token (start, end) character spans; specials
                have zero-length spans.
            token_attrs: Per-token attribution values toward the
                target emotion.

        Returns:
            Between one and five adjacent-word phrases with the strongest
            contribution, weights normalized to sum to 1.  Empty only
            when the text contains no word tokens.
        """

        @dataclass
        class _Word:
            text: str
            start: int
            end: int
            attr: float

        words: list[_Word] = []
        for i, (start, end) in enumerate(offsets):
            if end <= start:
                continue
            value = float(token_attrs[i])
            piece = text[start:end]
            if words and start == words[-1].end:
                words[-1].text += piece
                words[-1].end = end
                words[-1].attr += value
            else:
                words.append(_Word(piece, start, end, value))

        if not words:
            return []

        positives = [w for w in words if w.attr > 0]
        if positives:
            peak = max(w.attr for w in positives)
            keep = [
                w for w in positives
                if w.attr >= peak * _SIGNAL_CUTOFF_RATIO
            ]
        else:
            # Guarantee at least one signal: when no word has positive
            # attribution, surface the single most influential word.
            keep = [max(words, key=lambda w: w.attr)]

        phrases: list[_Word] = []
        for word in keep:
            if (
                phrases
                and word.start - phrases[-1].end <= 1
            ):
                phrases[-1].text += " " + word.text
                phrases[-1].end = word.end
                phrases[-1].attr += word.attr
            else:
                phrases.append(_Word(word.text, word.start, word.end, word.attr))

        phrases.sort(key=lambda p: p.attr, reverse=True)
        top = phrases[:5]
        total = sum(p.attr for p in top) or 1.0
        return [
            EvidenceSignal(
                text=p.text,
                weight=round(p.attr / total, 3),
            )
            for p in top
        ]
