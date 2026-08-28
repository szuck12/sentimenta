# backend/app/core/emotions.py
# The GoEmotions taxonomy: all 28 labels plus Sentimenta's display
# metadata (emoji, plain-language description) and profile grouping.

from enum import Enum


class EmotionGroup(str, Enum):
    """Sentimenta's visualisation groups for the 27 GoEmotions labels.

    Note:
        These groupings are a Sentimenta presentation layer, not an
        official part of the GoEmotions dataset. They exist to give
        users an intuitive overview of the full 28-emotion output.
    """

    POSITIVE = "positive"
    NEGATIVE = "negative"
    COGNITIVE = "cognitive"
    NEUTRAL = "neutral"


class Emotion(str, Enum):
    """All 28 GoEmotions labels (27 emotions + neutral).

    The values exactly match the label order used by
    ``SamLowe/roberta-base-go_emotions``, so enum membership doubles as
    the canonical id-to-label mapping.
    """

    ADMIRATION = "admiration"
    AMUSEMENT = "amusement"
    ANGER = "anger"
    ANNOYANCE = "annoyance"
    APPROVAL = "approval"
    CARING = "caring"
    CONFUSION = "confusion"
    CURIOSITY = "curiosity"
    DESIRE = "desire"
    DISAPPOINTMENT = "disappointment"
    DISAPPROVAL = "disapproval"
    DISGUST = "disgust"
    EMBARRASSMENT = "embarrassment"
    EXCITEMENT = "excitement"
    FEAR = "fear"
    GRATITUDE = "gratitude"
    GRIEF = "grief"
    JOY = "joy"
    LOVE = "love"
    NERVOUSNESS = "nervousness"
    OPTIMISM = "optimism"
    PRIDE = "pride"
    REALIZATION = "realization"
    RELIEF = "relief"
    REMORSE = "remorse"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"


EMOJIS: dict[Emotion, str] = {
    Emotion.ADMIRATION: "👏",
    Emotion.AMUSEMENT: "😄",
    Emotion.ANGER: "😠",
    Emotion.ANNOYANCE: "😒",
    Emotion.APPROVAL: "👍",
    Emotion.CARING: "🤗",
    Emotion.CONFUSION: "🤔",
    Emotion.CURIOSITY: "🧐",
    Emotion.DESIRE: "✨",
    Emotion.DISAPPOINTMENT: "😞",
    Emotion.DISAPPROVAL: "👎",
    Emotion.DISGUST: "🤢",
    Emotion.EMBARRASSMENT: "😳",
    Emotion.EXCITEMENT: "🤩",
    Emotion.FEAR: "😨",
    Emotion.GRATITUDE: "🙏",
    Emotion.GRIEF: "💔",
    Emotion.JOY: "😊",
    Emotion.LOVE: "❤️",
    Emotion.NERVOUSNESS: "😬",
    Emotion.OPTIMISM: "🌤️",
    Emotion.PRIDE: "🏆",
    Emotion.REALIZATION: "💡",
    Emotion.RELIEF: "😌",
    Emotion.REMORSE: "😔",
    Emotion.SADNESS: "😢",
    Emotion.SURPRISE: "😲",
    Emotion.NEUTRAL: "😐",
}

DESCRIPTIONS: dict[Emotion, str] = {
    Emotion.ADMIRATION: "Recognising someone or something as impressive "
                        "or excellent.",
    Emotion.AMUSEMENT: "Finding something funny or entertaining.",
    Emotion.ANGER: "Strong feelings of displeasure or hostility.",
    Emotion.ANNOYANCE: "Mild irritation or being bothered by something.",
    Emotion.APPROVAL: "Expressing agreement or a favourable judgement.",
    Emotion.CARING: "Showing warmth, concern, or compassion for others.",
    Emotion.CONFUSION: "Feeling puzzled or unable to understand.",
    Emotion.CURIOSITY: "Wanting to learn or know more about something.",
    Emotion.DESIRE: "Hoping for or wanting something to happen.",
    Emotion.DISAPPOINTMENT: "Feeling let down when expectations are "
                            "not met.",
    Emotion.DISAPPROVAL: "Expressing disagreement or disfavour.",
    Emotion.DISGUST: "Feeling repelled or strongly put off.",
    Emotion.EMBARRASSMENT: "Feeling awkward, self-conscious, or ashamed.",
    Emotion.EXCITEMENT: "High energy and eager anticipation.",
    Emotion.FEAR: "Feeling afraid or worried about danger.",
    Emotion.GRATITUDE: "Thankfulness for help, kindness, or gifts.",
    Emotion.GRIEF: "Deep sorrow, often from loss.",
    Emotion.JOY: "Happiness and delight.",
    Emotion.LOVE: "Deep affection and attachment.",
    Emotion.NERVOUSNESS: "Anxiety or unease about what may happen.",
    Emotion.OPTIMISM: "Hopefulness that things will turn out well.",
    Emotion.PRIDE: "Satisfaction in one's own or others' achievements.",
    Emotion.REALIZATION: "A moment of sudden understanding.",
    Emotion.RELIEF: "Ease after a worry or difficulty passes.",
    Emotion.REMORSE: "Regret or guilt about something done.",
    Emotion.SADNESS: "Unhappiness or sorrow.",
    Emotion.SURPRISE: "Being startled by the unexpected.",
    Emotion.NEUTRAL: "No strong emotional signal detected.",
}

# Sentimenta's grouping of the 27 non-neutral labels into three broad
# conceptual families used by the emotional-profile visualisation.
GROUP_MEMBERS: dict[EmotionGroup, tuple[Emotion, ...]] = {
    EmotionGroup.POSITIVE: (
        Emotion.ADMIRATION,
        Emotion.AMUSEMENT,
        Emotion.APPROVAL,
        Emotion.CARING,
        Emotion.DESIRE,
        Emotion.EXCITEMENT,
        Emotion.GRATITUDE,
        Emotion.JOY,
        Emotion.LOVE,
        Emotion.OPTIMISM,
        Emotion.PRIDE,
        Emotion.RELIEF,
    ),
    EmotionGroup.NEGATIVE: (
        Emotion.ANGER,
        Emotion.ANNOYANCE,
        Emotion.DISAPPOINTMENT,
        Emotion.DISAPPROVAL,
        Emotion.DISGUST,
        Emotion.EMBARRASSMENT,
        Emotion.FEAR,
        Emotion.GRIEF,
        Emotion.NERVOUSNESS,
        Emotion.REMORSE,
        Emotion.SADNESS,
    ),
    EmotionGroup.COGNITIVE: (
        Emotion.CONFUSION,
        Emotion.CURIOSITY,
        Emotion.REALIZATION,
        Emotion.SURPRISE,
    ),
    EmotionGroup.NEUTRAL: (Emotion.NEUTRAL,),
}

GROUP_LABELS: dict[EmotionGroup, str] = {
    EmotionGroup.POSITIVE: "Positive & affiliative",
    EmotionGroup.NEGATIVE: "Negative & heavy",
    EmotionGroup.COGNITIVE: "Cognitive & ambiguous",
    EmotionGroup.NEUTRAL: "Neutral",
}

ALL_EMOTIONS: list[Emotion] = list(Emotion)


def group_of(emotion: Emotion) -> EmotionGroup:
    """Return the Sentimenta profile group an emotion belongs to.

    Args:
        emotion: Any of the 28 GoEmotions labels.

    Returns:
        The EmotionGroup containing ``emotion``.
    """
    for group, members in GROUP_MEMBERS.items():
        if emotion in members:
            return group
    raise ValueError(f"No group defined for emotion {emotion!r}")
