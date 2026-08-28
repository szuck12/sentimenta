# backend/app/services/explanation_service.py
# Evidence-based explanations: Captum integrated-gradients token
# attribution mapped back to words/phrases, plus factual,
# template-generated summaries built strictly from model outputs.

import logging
from dataclasses import dataclass

import torch
from captum.attr import LayerIntegratedGradients

from ..core.config import Settings
from ..core.emotions import Emotion
from ..schemas.analysis import EvidenceSignal, Explanation
from .emotion_model_service import EmotionModelService

logger = logging.getLogger(__name__)

# Words whose positive attribution falls below this fraction of the
# strongest word are not treated as evidence.
_SIGNAL_CUTOFF_RATIO = 0.15


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
        """Explain why ``prediction_scores`` favour a primary emotion.

        Args:
            text: The analysed input text.
            prediction_scores: Full 28-label probability mapping from
                the primary inference pass.

        Returns:
            An Explanation with the target label, a factual summary,
            and (when available) attributed key-signal phrases.
        """
        ranked = sorted(
            prediction_scores.items(), key=lambda kv: (-kv[1], kv[0])
        )
        target, target_score = ranked[0]
        others = [e for e, s in ranked[1:] if s >= self.settings.emotion_threshold][:2]

        if not self.settings.enable_attribution or not self.models.is_loaded:
            return self._probability_explanation(
                target, target_score, others
            )

        try:
            signals = self._attribute(text, target)
        except Exception as exc:
            logger.warning("Token attribution failed: %s", exc)
            return self._probability_explanation(
                target, target_score, others
            )

        return Explanation(
            summary=self._summary(target, target_score, others, True),
            signals=signals,
            method="integrated_gradients",
            target_label=target,
        )

    def _probability_explanation(
        self,
        target: Emotion,
        target_score: float,
        others: list[Emotion],
    ) -> Explanation:
        """Build the fallback explanation from probabilities alone."""
        return Explanation(
            summary=self._summary(target, target_score, others, False),
            signals=[],
            method="probabilities",
            target_label=target,
        )

    def _summary(
        self,
        target: Emotion,
        target_score: float,
        others: list[Emotion],
        has_signals: bool,
    ) -> str:
        """Render the human-facing summary without fabricating cause.

        Args:
            target: Primary emotion label.
            target_score: Its probability.
            others: Up to two further detected emotions.
            has_signals: Whether token evidence is included below.

        Returns:
            A one-to-two-sentence factual description.
        """
        pct = round(target_score * 100)
        parts = [f"Sentimenta detected {target.value} ({pct}% confidence)"]
        if others:
            names = " and ".join(e.value for e in others)
            parts.append(f"alongside signals of {names}")
        summary = ", ".join(parts) + "."
        if has_signals:
            summary += (
                " The highlighted words contributed most toward "
                "that reading."
            )
        else:
            summary += (
                " Token-level evidence is unavailable for this "
                "input."
            )
        return summary

    def _attribute(
        self, text: str, target: Emotion
    ) -> list[EvidenceSignal]:
        """Run integrated gradients and extract key phrases.

        Args:
            text: Input text (short enough for one model pass).
            target: The emotion output neuron to attribute against.

        Returns:
            Up to three phrases with normalised positive weights;
            empty list when no token supports the target emotion.

        Raises:
            RuntimeError: Propagated from the model service when the
                forward passes fail.
        """
        models = self.models
        assert models.model is not None and models.tokenizer is not None

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
            Up to three adjacent-word phrases with the strongest
            positive contribution, weights normalised to sum to 1.
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

        positives = [w for w in words if w.attr > 0]
        if not positives:
            return []
        peak = max(w.attr for w in positives)
        keep = [
            w for w in positives
            if w.attr >= peak * _SIGNAL_CUTOFF_RATIO
        ]

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
        top = phrases[:3]
        total = sum(p.attr for p in top) or 1.0
        return [
            EvidenceSignal(
                text=p.text,
                weight=round(p.attr / total, 3),
            )
            for p in top
        ]
