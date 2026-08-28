# backend/app/schemas/analysis.py
# Pydantic request/response models defining the public API contract.

from pydantic import BaseModel, Field

from ..core.emotions import Emotion, EmotionGroup


class EmotionScore(BaseModel):
    """A single emotion label paired with its model probability."""

    label: Emotion
    score: float = Field(
        ge=0.0, le=1.0, description="Sigmoid probability from the model."
    )


class Intensity(BaseModel):
    """Sentimenta-derived emotional-intensity metric.

    Note:
        Intensity is *not* predicted by GoEmotions. It is derived as
        ``1 - P(neutral)`` so that emotionally flat text scores low
        and strongly-signalled text scores high.
    """

    score: float = Field(ge=0.0, le=1.0)
    label: str = Field(description="One of: low, moderate, high.")


class Profile(BaseModel):
    """Emotional profile aggregated over Sentimenta's groups."""

    positive: float = Field(description="Sum of positive-group scores.")
    negative: float = Field(description="Sum of negative-group scores.")
    cognitive: float = Field(
        description="Sum of cognitive/ambiguous-group scores."
    )
    neutral: float = Field(description="Score of the neutral label.")
    shares: dict[EmotionGroup, float] = Field(
        description=(
            "Each group's fraction of the total signal, in [0, 1]; "
            "the four shares sum to 1."
        )
    )


class EvidenceSignal(BaseModel):
    """A phrase the explainer identified as supporting evidence."""

    text: str
    weight: float = Field(
        ge=-1.0,
        le=1.0,
        description=(
            "Attribution strength toward the target emotion; "
            "positive values support it."
        ),
    )


class Explanation(BaseModel):
    """Model-derived evidence plus a carefully-worded interpretation.

    The ``summary`` is template-generated strictly from model outputs;
    ``signals`` come from token attribution when available.
    """

    summary: str
    signals: list[EvidenceSignal] = Field(default_factory=list)
    method: str = Field(
        description=(
            "'integrated_gradients' when token attribution succeeded, "
            "otherwise 'probabilities'."
        )
    )
    target_label: Emotion


class SentenceAnalysis(BaseModel):
    """Independent emotion analysis of one sentence."""

    index: int = Field(ge=0)
    text: str
    primary_emotion: EmotionScore
    emotions: list[EmotionScore] = Field(
        description="Detected emotions above the threshold, sorted."
    )


class AnalyzeMetadata(BaseModel):
    """Diagnostic information about a single analysis run."""

    model_id: str
    char_count: int
    word_count: int
    sentence_count: int
    threshold: float
    attribution_used: bool
    truncated_tokens: bool = Field(
        description=(
            "True when the input exceeded the model's token budget "
            "and was truncated before inference."
        )
    )
    latency_ms: dict[str, float] = Field(
        description=(
            "Wall-clock timings in milliseconds keyed by pipeline "
            "stage ('inference', 'explanation', 'total')."
        )
    )


class AnalyzeRequest(BaseModel):
    """Request body for POST /api/analyze."""

    text: str = Field(min_length=1, max_length=2000)
    include_sentences: bool = Field(
        default=False,
        description=(
            "Also analyse each sentence independently (up to the "
            "configured sentence limit)."
        ),
    )


class SentenceAnalysisRequest(BaseModel):
    """Request body for POST /api/analyze/sentences."""

    text: str = Field(min_length=1, max_length=2000)


class AnalyzeResponse(BaseModel):
    """Full single-text analysis result."""

    primary_emotion: EmotionScore
    emotions: list[EmotionScore] = Field(
        description=(
            "All emotions at or above the detection threshold, "
            "sorted by score descending (primary first)."
        )
    )
    all_emotions: list[EmotionScore] = Field(
        description=(
            "All 28 emotions sorted by score descending, for the "
            "full-spectrum visualisation."
        )
    )
    intensity: Intensity
    profile: Profile
    explanation: Explanation
    sentences: list[SentenceAnalysis] = Field(default_factory=list)
    metadata: AnalyzeMetadata


class SentenceAnalysisResponse(BaseModel):
    """Response body for POST /api/analyze/sentences."""

    sentences: list[SentenceAnalysis]
    metadata: AnalyzeMetadata


class HealthResponse(BaseModel):
    """Response body for GET /api/health."""

    status: str
    version: str
    model_id: str
    model_loaded: bool


class EmotionInfo(BaseModel):
    """Taxonomy entry for one emotion label."""

    label: Emotion
    emoji: str
    group: EmotionGroup
    description: str


class EmotionsResponse(BaseModel):
    """Response body for GET /api/emotions."""

    count: int
    groups: dict[str, str]
    emotions: list[EmotionInfo]


class ErrorBody(BaseModel):
    """Machine-readable error details."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Envelope used for every non-2xx API response."""

    error: ErrorBody
