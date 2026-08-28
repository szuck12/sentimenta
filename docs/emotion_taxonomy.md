# Emotion Taxonomy

Sentimenta classifies text across 28 emotions derived from the
GoEmotions dataset. This document defines the full taxonomy, the
grouping system, and how multi-label classification works in practice.

---

## 1. The 28 Emotions

GoEmotions defines 27 specific emotions plus a neutral class. Each
emotion is a distinct label — not a score on a spectrum, but an
independent binary assessment (present or not) with a continuous
confidence score.

### Positive & Affiliative (12 emotions)

| Label | Emoji | Description |
|-------|-------|-------------|
| admiration | 👏 | Recognising someone or something as impressive or excellent. |
| amusement | 😄 | Finding something funny or entertaining. |
| approval | 👍 | Expressing agreement or a favourable judgement. |
| caring | 🤗 | Showing warmth, concern, or compassion for others. |
| desire | ✨ | Hoping for or wanting something to happen. |
| excitement | 🤩 | High energy and eager anticipation. |
| gratitude | 🙏 | Thankfulness for help, kindness, or gifts. |
| joy | 😊 | Happiness and delight. |
| love | ❤️ | Deep affection and attachment. |
| optimism | 🌤️ | Hopefulness that things will turn out well. |
| pride | 🏆 | Satisfaction in one's own or others' achievements. |
| relief | 😌 | Ease after a worry or difficulty passes. |

### Negative & Heavy (11 emotions)

| Label | Emoji | Description |
|-------|-------|-------------|
| anger | 😠 | Strong feelings of displeasure or hostility. |
| annoyance | 😒 | Mild irritation or being bothered by something. |
| disappointment | 😞 | Feeling let down when expectations are not met. |
| disapproval | 👎 | Expressing disagreement or disfavour. |
| disgust | 🤢 | Feeling repelled or strongly put off. |
| embarrassment | 😳 | Feeling awkward, self-conscious, or ashamed. |
| fear | 😨 | Feeling afraid or worried about danger. |
| grief | 💔 | Deep sorrow, often from loss. |
| nervousness | 😬 | Anxiety or unease about what may happen. |
| remorse | 😔 | Regret or guilt about something done. |
| sadness | 😢 | Unhappiness or sorrow. |

### Cognitive & Ambiguous (4 emotions)

| Label | Emoji | Description |
|-------|-------|-------------|
| confusion | 🤔 | Feeling puzzled or unable to understand. |
| curiosity | 🧐 | Wanting to learn or know more about something. |
| realization | 💡 | A moment of sudden understanding. |
| surprise | 😲 | Being startled by the unexpected. |

### Neutral (1 emotion)

| Label | Emoji | Description |
|-------|-------|-------------|
| neutral | 😐 | No strong emotional signal detected. |

---

## 2. Group Definitions

### Why Groups Exist

The 28 emotions are individually meaningful, but presenting all 28 as
an undifferentiated list can be overwhelming. Groups provide a
higher-level summary that helps users quickly understand the emotional
character of their text.

### Group Membership

Groups are defined in `core/emotions.py` via `GROUP_MEMBERS`:

```python
GROUP_MEMBERS: dict[EmotionGroup, tuple[Emotion, ...]] = {
    EmotionGroup.POSITIVE: (
        Emotion.ADMIRATION, Emotion.AMUSEMENT, Emotion.APPROVAL,
        Emotion.CARING, Emotion.DESIRE, Emotion.EXCITEMENT,
        Emotion.GRATITUDE, Emotion.JOY, Emotion.LOVE,
        Emotion.OPTIMISM, Emotion.PRIDE, Emotion.RELIEF,
    ),
    EmotionGroup.NEGATIVE: (
        Emotion.ANGER, Emotion.ANNOYANCE, Emotion.DISAPPOINTMENT,
        Emotion.DISAPPROVAL, Emotion.DISGUST, Emotion.EMBARRASSMENT,
        Emotion.FEAR, Emotion.GRIEF, Emotion.NERVOUSNESS,
        Emotion.REMORSE, Emotion.SADNESS,
    ),
    EmotionGroup.COGNITIVE: (
        Emotion.CONFUSION, Emotion.CURIOSITY,
        Emotion.REALIZATION, Emotion.SURPRISE,
    ),
    EmotionGroup.NEUTRAL: (Emotion.NEUTRAL,),
}
```

### Rationale

| Group | Members | Rationale |
|-------|---------|-----------|
| **Positive & affiliative** | 12 | Emotions that signal well-being, connection, or favourable states. They tend to co-occur in texts expressing happiness, gratitude, or social bonding. |
| **Negative & heavy** | 11 | Emotions that signal distress, displeasure, or aversive states. They tend to co-occur in texts expressing pain, conflict, or loss. |
| **Cognitive & ambiguous** | 4 | Emotions that are information-processing states rather than clearly positive or negative. Confusion and curiosity can lead anywhere; surprise can be pleasant or unpleasant. |
| **Neutral** | 1 | The absence of a strong emotional signal. Used as the baseline for intensity computation. |

### Important Note

> These groupings are a Sentimenta presentation layer, not an official
> part of the GoEmotions dataset. They exist to give users an intuitive
> overview of the full 28-emotion output.

This note appears in the `EmotionGroup` enum docstring and on the
How It Works page.

---

## 3. How Groups Are Used

### Profile Visualization

The emotional profile sums each group's member scores and normalises
them to shares that sum to 1.0:

```json
{
  "profile": {
    "positive": 2.09,
    "negative": 0.04,
    "cognitive": 0.03,
    "neutral": 0.07,
    "shares": {
      "positive": 0.93,
      "negative": 0.02,
      "cognitive": 0.01,
      "neutral": 0.03
    }
  }
}
```

The `shares` are used by the frontend to render proportional
visualisations (e.g. a bar chart or pie chart showing the emotional
composition).

### Color Coding

Each group has a distinct color used across the UI:

| Group | Color | Used in |
|-------|-------|---------|
| Positive | Coral/Orange | Badge variant, journey timeline dots, bar fills |
| Negative | Rose | Badge variant, journey timeline dots |
| Cognitive | Lavender/Violet | Badge variant, journey timeline dots |
| Neutral | Sand/Slate | Badge variant, journey timeline dots |

The colors are defined in `lib/types.ts`:

```typescript
export const EMOTION_COLORS: Record<string, string> = {
  positive: '#F97D4D',
  negative: '#F47B82',
  cognitive: '#A78BFA',
  neutral: '#C5B9A8',
}
```

### Journey Timeline

The `JourneyCard` uses group colors for the vertical timeline dots and
connecting lines. Each sentence's primary emotion determines its color:

```typescript
function lineColor(label: string): string {
  if (POSITIVE_LABELS.includes(label)) return 'bg-coral-400'
  if (NEGATIVE_LABELS.includes(label)) return 'bg-rose-400'
  if (COGNITIVE_LABELS.includes(label)) return 'bg-lavender-400'
  return 'bg-sand-400'
}
```

### Emotions Page

The `/emotions` page fetches the full taxonomy from `GET /api/emotions`
and renders emotions grouped by category. Each group has a heading with
the group's display label (e.g. "Positive & affiliative"), and the
emotions are displayed in a responsive grid.

---

## 4. Multi-Label Nature

### Why Multiple Emotions Co-Occur

GoEmotions is a multi-label classification task. Unlike single-label
classifiers (which force exactly one output), multi-label classifiers
assess each label independently:

- A sigmoid activation produces one probability per label.
- Probabilities do not sum to 1.
- Multiple labels can have high scores simultaneously.

This reflects how humans actually experience emotions: a single text
can express joy, gratitude, and excitement at the same time.

### How Sentimenta Presents Multi-Label Output

1. **Primary emotion**: The single highest-scoring label. Always shown
   prominently in the `PrimaryEmotionCard`.

2. **Detected emotions**: All labels scoring at or above the threshold
   (default 0.30). Shown in the `EmotionMixCard` with horizontal bars.

3. **Full spectrum**: All 28 labels sorted by score, shown in the
   collapsible `SpectrumCard`. This lets users see the full picture,
   including low-scoring emotions that may still be interesting.

---

## 5. Examples of Multi-Emotion Texts

### Example 1: "I'm nervous but excited!"

Likely high scores:
- `nervousness` (anxiety about the unknown)
- `excitement` (eager anticipation)
- Possibly `optimism` (hopeful undertone)

### Example 2: "Thank you so much for helping me move this weekend."

Likely high scores:
- `gratitude` (thankfulness)
- `caring` (acknowledging someone's effort)
- Possibly `love` (affection for the helper)

### Example 3: "I can't believe they did that."

Likely high scores:
- `surprise` (unexpected event)
- Possibly `disapproval` or `anger` depending on context
- Possibly `disappointment` if negative

### Example 4: "I'm so happy we finally got to spend time together."

Likely high scores:
- `joy` (happiness)
- `love` (affection)
- `relief` (the "finally" suggests prior frustration)
- Possibly `gratitude`

### Example 5: "I shouldn't have said that to her, I feel terrible."

Likely high scores:
- `remorse` (regret)
- `sadness` (emotional pain)
- Possibly `disappointment` (in oneself)

---

## 6. Common Co-occurrence Patterns

Based on the model's behaviour and the semantic relationships between
emotions:

| Primary | Often co-occurs with | Why |
|---------|---------------------|-----|
| joy | excitement, love, gratitude | Positive states cluster together |
| sadness | grief, disappointment, remorse | Negative states often compound |
| anger | annoyance, disgust, disapproval | Hostility spectrum |
| fear | nervousness, confusion | Threat-related states |
| excitement | joy, optimism, desire | Anticipation-related states |
| surprise | confusion, realization | Unexpected-event states |
| gratitude | love, joy, caring | Affiliative states |
| curiosity | confusion, desire | Information-seeking states |
| pride | joy, approval, excitement | Achievement states |
| relief | joy, optimism | Post-stress resolution |

### Asymmetric Pairs

Some emotions are related but rarely co-occur at high scores:

- `joy` vs `sadness`: Typically one dominates.
- `anger` vs `fear`: Different threat responses.
- `excitement` vs `nervousness`: Can co-occur ("nervous excitement")
  but often one is dominant.
- `admiration` vs `disapproval`: Opposing evaluative states.

---

## 7. The Neutral Class

`neutral` serves two purposes:

1. **Classification**: Text with no strong emotional signal (e.g. "The
   package arrived on Tuesday") scores high on neutral.

2. **Intensity computation**: The neutral score is used to derive
   emotional intensity: `intensity = 1 - P(neutral)`. A high neutral
   score means low emotional intensity; a low neutral score means high
   intensity.

### Neutral vs Low Scores

A text can have low scores across all 28 emotions without any single
emotion being dominant. This is different from high neutral:

- **High neutral** (P(neutral) > 0.65): The model is confident there
  is no emotional signal. Intensity is "low".
- **Low everything** (all scores < 0.15): The model is uncertain.
  Neutral may still be the highest, but the intensity calculation
  treats this as moderate.

---

## 8. Label Order

The 28 labels in the `Emotion` enum follow the exact order used by
`SamLowe/roberta-base-go_emotions`. This ordering is significant:

- The model's `id2label` config maps integer indices to label strings.
- Sentimenta's `Emotion` enum values match these strings exactly.
- During loading, `EmotionModelService.load()` validates that the
  model's label set matches the enum, catching any mismatch early.

The canonical order (as defined in `core/emotions.py`):

```
admiration, amusement, anger, annoyance, approval, caring,
confusion, curiosity, desire, disappointment, disapproval,
disgust, embarrassment, excitement, fear, gratitude, grief,
joy, love, nervousness, optimism, pride, realization, relief,
remorse, sadness, surprise, neutral
```
