# backend/app/services/analysis_service.py
# Orchestrates a full analysis: preprocessing, model inference,
# derived metrics, explanations, and optional sentence-level passes.

import time

from ..core.config import Settings
from ..core.errors import EmptyTextError, ModelUnavailableError
from ..schemas.analysis import (
    AnalyzeMetadata,
    AnalyzeResponse,
    EmotionScore,
    SentenceAnalysis,
    SentenceAnalysisResponse,
)
from . import metrics
from .emotion_model_service import EmotionModelService
from .explanation_service import ExplanationService
from .preprocessing import (
    count_words,
    normalize_text,
    split_sentences,
)


class AnalysisService:
    """High-level analysis pipeline used by the API routes.

    Dependencies are injected so tests can substitute lightweight
    fakes for the PyTorch-backed model service.
    """

    def __init__(
        self,
        model_service: EmotionModelService,
        explanation_service: ExplanationService,
        settings: Settings,
    ) -> None:
        self.models = model_service
        self.explainer = explanation_service
        self.settings = settings

    def _require_model(self) -> None:
        """Reject requests until the model has finished loading."""
        if not self.models.is_loaded:
            raise ModelUnavailableError()

    def analyze(self, text: str, include_sentences: bool) -> AnalyzeResponse:
        """Analyse one block of text end-to-end.

        Args:
            text: Raw user input (already length-validated).
            include_sentences: When True, also analyse each sentence
                independently (bounded by ``sentence_limit``).

        Returns:
            The complete response payload for POST /api/analyze.

        Raises:
            EmptyTextError: If nothing usable remains after
                normalisation.
            ModelUnavailableError: If the model is still loading.
        """
        started = time.perf_counter()
        normalized = normalize_text(text)
        if not normalized:
            raise EmptyTextError()
        self._require_model()

        scores = self.models.predict([normalized])[0]
        inference_ms = (time.perf_counter() - started) * 1000.0

        ranked = metrics.rank_emotions(scores)
        detected = metrics.detected_emotions(
            ranked, self.settings.emotion_threshold
        )
        primary_label, primary_score = ranked[0]
        intensity = metrics.compute_intensity(scores)
        profile = metrics.compute_profile(scores)

        all_emotions = [
            EmotionScore(label=e, score=round(s, 4))
            for e, s in ranked
        ]

        explanation_started = time.perf_counter()
        explanation = self.explainer.explain(normalized, scores)
        explanation_ms = (
            time.perf_counter() - explanation_started
        ) * 1000.0

        sentences: list[SentenceAnalysis] = []
        if include_sentences:
            sentences = self._analyze_sentences(normalized)

        return AnalyzeResponse(
            primary_emotion=EmotionScore(
                label=primary_label, score=round(primary_score, 4)
            ),
            emotions=[
                EmotionScore(label=e, score=round(s, 4))
                for e, s in detected
            ],
            all_emotions=all_emotions,
            intensity=intensity,
            profile=profile,
            explanation=explanation,
            sentences=sentences,
            metadata=self._metadata(
                raw_text=text,
                truncated=self.models.exceeds_token_budget(normalized),
                sentence_count=len(split_sentences(text)),
                attribution_used=(
                    explanation.method == "integrated_gradients"
                ),
                inference_ms=inference_ms,
                explanation_ms=explanation_ms,
                total_ms=(time.perf_counter() - started) * 1000.0,
            ),
        )

    def analyze_sentences(self, text: str) -> SentenceAnalysisResponse:
        """Analyse each sentence of ``text`` independently.

        Args:
            text: Raw user input.

        Returns:
            Per-sentence analyses in original order plus metadata.
        """
        started = time.perf_counter()
        normalized = normalize_text(text)
        if not normalized:
            raise EmptyTextError()
        self._require_model()

        sentences = self._analyze_sentences(normalized)
        total_ms = (time.perf_counter() - started) * 1000.0
        metadata = self._metadata(
            raw_text=text,
            sentence_count=len(split_sentences(text)),
            attribution_used=False,
            inference_ms=total_ms,
            explanation_ms=0.0,
            total_ms=total_ms,
            truncated=self.models.exceeds_token_budget(normalized),
        )
        return SentenceAnalysisResponse(
            sentences=sentences, metadata=metadata
        )

    def _analyze_sentences(
        self, normalized: str
    ) -> list[SentenceAnalysis]:
        """Batch-analyse up to ``sentence_limit`` sentences.

        Args:
            normalized: Whitespace-normalised full input.

        Returns:
            One SentenceAnalysis per processed sentence with its own
            threshold-filtered emotion list.
        """
        parts = split_sentences(normalized)[
            : self.settings.sentence_limit
        ]
        if not parts:
            return []
        batch_scores = self.models.predict(parts)
        results: list[SentenceAnalysis] = []
        for i, (part, scores) in enumerate(zip(parts, batch_scores)):
            ranked = metrics.rank_emotions(scores)
            detected = metrics.detected_emotions(
                ranked, self.settings.emotion_threshold
            )
            top_label, top_score = ranked[0]
            results.append(
                SentenceAnalysis(
                    index=i,
                    text=part,
                    primary_emotion=EmotionScore(
                        label=top_label, score=round(top_score, 4)
                    ),
                    emotions=[
                        EmotionScore(label=e, score=round(s, 4))
                        for e, s in detected
                    ],
                )
            )
        return results

    def _metadata(
        self,
        raw_text: str,
        sentence_count: int,
        attribution_used: bool,
        inference_ms: float,
        explanation_ms: float,
        total_ms: float,
        truncated: bool = False,
    ) -> AnalyzeMetadata:
        """Assemble response metadata; no user text is ever logged."""
        return AnalyzeMetadata(
            model_id=self.settings.model_id,
            char_count=len(raw_text),
            word_count=count_words(raw_text),
            sentence_count=sentence_count,
            threshold=self.settings.emotion_threshold,
            attribution_used=attribution_used,
            truncated_tokens=truncated,
            latency_ms={
                "inference": round(inference_ms, 1),
                "explanation": round(explanation_ms, 1),
                "total": round(total_ms, 1),
            },
        )
