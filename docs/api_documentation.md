# API Documentation

Sentimenta exposes a REST API under the `/api` prefix. All endpoints
accept and return JSON. The backend runs on port 8000 by default; the
Vite dev server proxies `/api` requests to it.

---

## Base URL

```
http://localhost:8000
```

In development, the frontend accesses the API through Vite's dev proxy
(`/api` → `http://127.0.0.1:8000`), so no base URL is needed in client
code.

---

## Error Envelope

Every non-2xx response follows a single envelope:

```json
{
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

The `code` field is machine-readable and stable. The `message` field is
human-readable and safe to display to users.

### Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| `empty_text` | 422 | Submitted text is empty or whitespace-only after normalization. |
| `text_too_long` | 422 | Text exceeds `SENTIMENTA_MAX_TEXT_CHARS` (default 2000). |
| `model_unavailable` | 503 | The emotion model is still loading at startup. |
| `invalid_request` | 422 | Pydantic validation failed (missing field, wrong type, etc.). |
| `internal_error` | 500 | An unexpected server error occurred. |

---

## Validation Errors

When Pydantic rejects the request body, the `invalid_request` envelope
is returned with the first validation error's field and message:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "text: Field required"
  }
}
```

The field name is extracted from the Pydantic error's `loc` array and
prepended to the message.

---

## Character Limit

All text inputs are limited to **2,000 characters** by default
(configurable via `SENTIMENTA_MAX_TEXT_CHARS`). The frontend character
counter enforces the same limit, turning red when exceeded.

---

## Endpoints

### GET /api/health

Returns service liveness and model status.

**Response: 200 OK**

```json
{
  "status": "ok",
  "version": "1.3.2",
  "model_loaded": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always `"ok"` when the server is reachable. |
| `version` | string | Application version from `Settings.version`. |
| `model_loaded` | boolean | `true` when the model weights are loaded and ready. |

---

### GET /api/emotions

Returns the full GoEmotions taxonomy with Sentimenta display metadata.

**Response: 200 OK**

```json
{
  "count": 28,
  "groups": {
    "positive": "Positive & affiliative",
    "negative": "Negative & heavy",
    "cognitive": "Cognitive & ambiguous",
    "neutral": "Neutral"
  },
  "emotions": [
    {
      "label": "admiration",
      "emoji": "👏",
      "group": "positive",
      "description": "Recognising someone or something as impressive or excellent."
    },
    {
      "label": "amusement",
      "emoji": "😄",
      "group": "positive",
      "description": "Finding something funny or entertaining."
    },
    {
      "label": "anger",
      "emoji": "😠",
      "group": "negative",
      "description": "Strong feelings of displeasure or hostility."
    },
    {
      "label": "annoyance",
      "emoji": "😒",
      "group": "negative",
      "description": "Mild irritation or being bothered by something."
    },
    {
      "label": "approval",
      "emoji": "👍",
      "group": "positive",
      "description": "Expressing agreement or a favorable judgement."
    },
    {
      "label": "caring",
      "emoji": "🤗",
      "group": "positive",
      "description": "Showing warmth, concern, or compassion for others."
    },
    {
      "label": "confusion",
      "emoji": "🤔",
      "group": "cognitive",
      "description": "Feeling puzzled or unable to understand."
    },
    {
      "label": "curiosity",
      "emoji": "🧐",
      "group": "cognitive",
      "description": "Wanting to learn or know more about something."
    },
    {
      "label": "desire",
      "emoji": "✨",
      "group": "positive",
      "description": "Hoping for or wanting something to happen."
    },
    {
      "label": "disappointment",
      "emoji": "😞",
      "group": "negative",
      "description": "Feeling let down when expectations are not met."
    },
    {
      "label": "disapproval",
      "emoji": "👎",
      "group": "negative",
      "description": "Expressing disagreement or disfavor."
    },
    {
      "label": "disgust",
      "emoji": "🤢",
      "group": "negative",
      "description": "Feeling repelled or strongly put off."
    },
    {
      "label": "embarrassment",
      "emoji": "😳",
      "group": "negative",
      "description": "Feeling awkward, self-conscious, or ashamed."
    },
    {
      "label": "excitement",
      "emoji": "🤩",
      "group": "positive",
      "description": "High energy and eager anticipation."
    },
    {
      "label": "fear",
      "emoji": "😨",
      "group": "negative",
      "description": "Feeling afraid or worried about danger."
    },
    {
      "label": "gratitude",
      "emoji": "🙏",
      "group": "positive",
      "description": "Thankfulness for help, kindness, or gifts."
    },
    {
      "label": "grief",
      "emoji": "💔",
      "group": "negative",
      "description": "Deep sorrow, often from loss."
    },
    {
      "label": "joy",
      "emoji": "😊",
      "group": "positive",
      "description": "Happiness and delight."
    },
    {
      "label": "love",
      "emoji": "❤️",
      "group": "positive",
      "description": "Deep affection and attachment."
    },
    {
      "label": "nervousness",
      "emoji": "😬",
      "group": "negative",
      "description": "Anxiety or unease about what may happen."
    },
    {
      "label": "optimism",
      "emoji": "🌤️",
      "group": "positive",
      "description": "Hopefulness that things will turn out well."
    },
    {
      "label": "pride",
      "emoji": "🏆",
      "group": "positive",
      "description": "Satisfaction in one's own or others' achievements."
    },
    {
      "label": "realization",
      "emoji": "💡",
      "group": "cognitive",
      "description": "A moment of sudden understanding."
    },
    {
      "label": "relief",
      "emoji": "😌",
      "group": "positive",
      "description": "Ease after a worry or difficulty passes."
    },
    {
      "label": "remorse",
      "emoji": "😔",
      "group": "negative",
      "description": "Regret or guilt about something done."
    },
    {
      "label": "sadness",
      "emoji": "😢",
      "group": "negative",
      "description": "Unhappiness or sorrow."
    },
    {
      "label": "surprise",
      "emoji": "😲",
      "group": "cognitive",
      "description": "Being startled by the unexpected."
    },
    {
      "label": "neutral",
      "emoji": "😐",
      "group": "neutral",
      "description": "No strong emotional signal detected."
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `count` | integer | Total number of emotions (always 28). |
| `groups` | object | Map of group key → display label. |
| `emotions` | array | All 28 emotions with label, emoji, group, and description. |

---

### POST /api/analyze a single block of text.

**Request Body**

```json
{
  "text": "I finally got the job I've been hoping for!",
  "include_sentences": false
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | — | Input text. 1–2,000 characters. |
| `include_sentences` | boolean | No | `false` | Also analyze each sentence independently (up to 10). |

**Response: 200 OK**

```json
{
  "primary_emotion": {
    "label": "excitement",
    "score": 0.7832
  },
  "emotions": [
    { "label": "excitement", "score": 0.7832 },
    { "label": "joy", "score": 0.6214 },
    { "label": "optimism", "score": 0.4105 }
  ],
  "all_emotions": [
    { "label": "excitement", "score": 0.7832 },
    { "label": "joy", "score": 0.6214 },
    { "label": "optimism", "score": 0.4105 },
    { "label": "desire", "score": 0.1843 },
    { "label": "neutral", "score": 0.0712 },
    { "label": "admiration", "score": 0.0534 },
    { "label": "love", "score": 0.0421 },
    { "label": "pride", "score": 0.0318 },
    { "label": "caring", "score": 0.0210 },
    { "label": "gratitude", "score": 0.0198 },
    { "label": "amusement", "score": 0.0176 },
    { "label": "approval", "score": 0.0142 },
    { "label": "relief", "score": 0.0130 },
    { "label": "curiosity", "score": 0.0112 },
    { "label": "surprise", "score": 0.0098 },
    { "label": "realization", "score": 0.0087 },
    { "label": "confusion", "score": 0.0076 },
    { "label": "nervousness", "score": 0.0065 },
    { "label": "sadness", "score": 0.0054 },
    { "label": "annoyance", "score": 0.0043 },
    { "label": "disappointment", "score": 0.0038 },
    { "label": "remorse", "score": 0.0032 },
    { "label": "fear", "score": 0.0028 },
    { "label": "disapproval", "score": 0.0024 },
    { "label": "anger", "score": 0.0021 },
    { "label": "grief", "score": 0.0018 },
    { "label": "disgust", "score": 0.0015 },
    { "label": "embarrassment", "score": 0.0012 }
  ],
  "intensity": {
    "score": 0.9288,
    "label": "high"
  },
  "profile": {
    "positive": 2.0857,
    "negative": 0.0415,
    "cognitive": 0.0297,
    "neutral": 0.0712,
    "shares": {
      "positive": 0.9263,
      "negative": 0.0184,
      "cognitive": 0.0132,
      "neutral": 0.0316
    }
  },
  "explanation": {
    "summary": "Sentimenta detected excitement (78% confidence), alongside signals of joy and optimism. The highlighted words contributed most toward that reading.",
    "signals": [
      { "text": "finally got the job", "weight": 0.512 },
      { "text": "hoping for", "weight": 0.324 },
      { "text": "!", "weight": 0.164 }
    ],
    "method": "integrated_gradients",
    "target_label": "excitement"
  },
  "sentences": [],
  "metadata": {
    "model_id": "SamLowe/roberta-base-go_emotions",
    "char_count": 45,
    "word_count": 8,
    "sentence_count": 1,
    "threshold": 0.3,
    "attribution_used": true,
    "truncated_tokens": false,
    "latency_ms": {
      "inference": 45.2,
      "explanation": 120.8,
      "total": 166.3
    }
  }
}
```

**With `include_sentences: true`**

When enabled, the `sentences` array is populated:

```json
{
  "sentences": [
    {
      "index": 0,
      "text": "I was nervous at first.",
      "primary_emotion": { "label": "nervousness", "score": 0.6812 },
      "emotions": [
        { "label": "nervousness", "score": 0.6812 }
      ]
    },
    {
      "index": 1,
      "text": "Then I felt relieved!",
      "primary_emotion": { "label": "relief", "score": 0.7234 },
      "emotions": [
        { "label": "relief", "score": 0.7234 }
      ]
    }
  ]
}
```

**Error Responses**

| Status | Code | When |
|--------|------|------|
| 422 | `empty_text` | Text is empty or whitespace-only after normalization. |
| 422 | `text_too_long` | Text exceeds 2,000 characters. |
| 422 | `invalid_request` | Missing `text` field or wrong type. |
| 503 | `model_unavailable` | Model still loading (startup). |
| 500 | `internal_error` | Unexpected server error. |

---

### POST /api/analyze/sentences

Analyzes each sentence of the input independently. Useful for tracking
emotional shifts across a passage.

**Request Body**

```json
{
  "text": "I was nervous. Then I felt relieved!"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | Input text. 1–2,000 characters. Sentences are split automatically. |

**Response: 200 OK**

```json
{
  "sentences": [
    {
      "index": 0,
      "text": "I was nervous.",
      "primary_emotion": { "label": "nervousness", "score": 0.6812 },
      "emotions": [
        { "label": "nervousness", "score": 0.6812 }
      ]
    },
    {
      "index": 1,
      "text": "Then I felt relieved!",
      "primary_emotion": { "label": "relief", "score": 0.7234 },
      "emotions": [
        { "label": "relief", "score": 0.7234 }
      ]
    }
  ],
  "metadata": {
    "model_id": "SamLowe/roberta-base-go_emotions",
    "char_count": 36,
    "word_count": 6,
    "sentence_count": 2,
    "threshold": 0.3,
    "attribution_used": false,
    "truncated_tokens": false,
    "latency_ms": {
      "inference": 52.1,
      "explanation": 0.0,
      "total": 52.1
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `sentences` | array | Per-sentence analysis results in original order. |
| `sentences[].index` | integer | Zero-based position in the input. |
| `sentences[].text` | string | The sentence text (whitespace-normalized). |
| `sentences[].primary_emotion` | EmotionScore | Highest-scoring emotion for this sentence. |
| `sentences[].emotions` | EmotionScore[] | All emotions at or above the detection threshold. |
| `metadata` | AnalyzeMetadata | Processing metadata (same schema as `/api/analyze`). |

**Note**: Attribution is **not** run for sentence-level analysis (the
`method` in the explanation defaults to `"probabilities"` and
`attribution_used` is `false`). The sentence limit is 10, controlled by
`SENTIMENTA_SENTENCE_LIMIT`.

---

## Schema Definitions

### EmotionScore

```json
{
  "label": "joy",
  "score": 0.85
}
```

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `label` | string | — | One of the 28 GoEmotions labels. |
| `score` | float | 0.0–1.0 | Sigmoid probability from the model. |

### Intensity

```json
{
  "score": 0.90,
  "label": "high"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `score` | float | `1 - P(neutral)`, clamped to [0, 1]. |
| `label` | string | One of `"low"` (< 0.35), `"moderate"` (0.35–0.65), `"high"` (>= 0.65). |

### Profile

```json
{
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
```

Each group value is the sum of its member emotions' sigmoid
probabilities. Shares are normalized to sum to 1.0.

### Explanation

```json
{
  "summary": "Sentimenta detected joy (85% confidence).",
  "signals": [
    { "text": "so happy", "weight": 0.65 },
    { "text": "finally", "weight": 0.35 }
  ],
  "method": "integrated_gradients",
  "target_label": "joy"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Template-generated factual description from model outputs. |
| `signals` | EvidenceSignal[] | Up to 3 key phrases with normalized weights. Empty when attribution is unavailable. |
| `method` | string | `"integrated_gradients"` or `"probabilities"`. |
| `target_label` | string | The primary emotion being explained. |

### EvidenceSignal

```json
{
  "text": "so happy",
  "weight": 0.65
}
```

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `text` | string | — | A phrase from the input text. |
| `weight` | float | -1.0–1.0 | Attribution strength. Positive values support the target emotion. Weights across all signals are normalized to sum to 1.0. |
