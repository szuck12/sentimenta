# ML Model Guide

Sentimenta's emotion classification is powered by a fine-tuned RoBERTa
model trained on Google's GoEmotions dataset. This document covers the
dataset, model architecture, inference pipeline, derived metrics,
attribution method, and known limitations.

---

## 1. GoEmotions Dataset

- **Source**: Google Research, published 2022.
- **Content**: 58,000 Reddit comments manually annotated by multiple
  annotators.
- **Labels**: 27 emotion categories + 1 neutral class (28 total).
- **Annotation scheme**: Multi-label — each comment can carry more than
  one emotion label.
- **License**: Creative Commons Attribution 4.0 (CC BY 4.0).

The dataset was collected from Reddit across a range of subreddits to
capture diverse emotional expression. Annotators were given the full
list of 27 emotions and asked to select all that applied, plus a
"neutral" option for comments with no clear emotional signal.

---

## 2. SamLowe/roberta-base-go_emotions

- **Model**: RoBERTa-base (125M parameters) fine-tuned on GoEmotions.
- **Author**: Sam Lowe (Hugging Face).
- **License**: MIT.
- **Model ID**: `SamLowe/roberta-base-go_emotions`.
- **Task**: Multi-label sequence classification.
- **Output**: 28 sigmoid-activated probabilities (one per label).

This model is loaded once at startup by `EmotionModelService` and
served as a singleton for the application's lifetime.

---

## 3. Model Architecture

```
Input text
    │
    ▼
Tokenizer (RoBERTa BPE)
    │  → input_ids, attention_mask
    │  → truncation to 256 tokens
    │
    ▼
RoBERTa-base encoder (12 layers, 768 hidden, 12 heads)
    │  → hidden states (batch, seq_len, 768)
    │
    ▼
Linear head (768 → 28)
    │  → logits (batch, 28)
    │
    ▼
Sigmoid activation
    │  → probabilities (batch, 28), each in [0, 1]
    │
    ▼
Output: dict[Emotion, float]
```

Key architectural points:

- **Sigmoid, not softmax**: Each label is scored independently. Scores
  do not sum to 1. Multiple labels can (and often do) have high
  probabilities simultaneously.
- **No aggregation layer**: There is no mechanism to enforce mutual
  exclusivity. This is by design — GoEmotions is a multi-label task.

---

## 4. Multi-Label vs Single-Label

Most sentiment classifiers output a single label (positive / negative /
neutral). GoEmotions is fundamentally different:

- A comment like "I'm nervous but excited!" legitimately expresses two
  emotions at once.
- The model independently assesses each of the 28 labels. A score of
  0.7 for `nervousness` and 0.6 for `excitement` means the model
  believes both emotions are present.
- Sentimenta's `emotions` array (filtered at the detection threshold)
  lists all emotions the model considers present, not just the top one.

This is why the response includes both `primary_emotion` (the single
highest-scoring label) and `emotions` (all labels above threshold).

---

## 5. The 28 Labels

### Positive & Affiliative (12)

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

### Negative & Heavy (11)

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

### Cognitive & Ambiguous (4)

| Label | Emoji | Description |
|-------|-------|-------------|
| confusion | 🤔 | Feeling puzzled or unable to understand. |
| curiosity | 🧐 | Wanting to learn or know more about something. |
| realization | 💡 | A moment of sudden understanding. |
| surprise | 😲 | Being startled by the unexpected. |

### Neutral (1)

| Label | Emoji | Description |
|-------|-------|-------------|
| neutral | 😐 | No strong emotional signal detected. |

**Note**: These groups are Sentimenta's presentation layer. They are
not part of the GoEmotions dataset's official taxonomy. See
[emotion_taxonomy.md](emotion_taxonomy.md) for the full rationale.

---

## 6. Threshold Semantics

Sentimenta uses a detection threshold of **0.30** by default
(configurable via `SENTIMENTA_EMOTION_THRESHOLD`).

How it works:

- Every emotion with `score >= threshold` is included in the
  `emotions` array (the "detected" emotions).
- The `primary_emotion` is always the single highest-scoring label,
  regardless of threshold.
- An emotion with score 0.29 would be below threshold and excluded
  from `emotions` but still present in `all_emotions`.

The threshold is a **tuning parameter**, not an absolute boundary:

- The GoEmotions model was published with a threshold of 0.5, where it
  achieves an overall F1 of ~0.45.
- Sentimenta lowers this to 0.30 to increase recall — surfacing more
  emotions for the user to consider rather than hiding borderline signals.
- This is an explicit trade-off: lower threshold means more false
  positives but fewer missed emotions.
- The threshold value is included in the response `metadata` so clients
  can interpret results accordingly.

---

## 7. Inference Pipeline

### Tokenisation

```python
encoded = tokenizer(
    texts,
    padding=True,
    truncation=True,
    max_length=256,        # MAX_INPUT_TOKENS
    return_tensors="pt",
    return_offsets_mapping=with_offsets,  # True for attribution
)
```

- **Padding**: Batch inputs are padded to the longest sequence.
- **Truncation**: Inputs exceeding 256 tokens are truncated from the
  right. The `metadata.truncated_tokens` flag is set to `true` when
  this happens.
- **Offset mapping**: Returned only for attribution requests (used to
  map token-level attributions back to word positions).

### Forward Pass

```python
logits = model(input_ids=ids, attention_mask=mask).logits
probs = torch.sigmoid(logits)   # (batch, 28)
```

- The model outputs raw logits. Sigmoid converts them to independent
  probabilities in [0, 1].
- A `threading.Lock` serialises forward passes for thread safety.
- The `forward_locked` method is exposed for Captum attribution, which
  runs many small forward passes with gradients enabled.

### Device Selection

```python
device = torch.device(
    settings.device
    if settings.device
    else ("mps" if torch.backends.mps.is_available() else "cpu")
)
```

On Apple Silicon, the model runs on the Metal Performance Shaders (MPS)
backend for faster inference. On other platforms, CPU is used. The device
can be overridden via `SENTIMENTA_DEVICE`.

---

## 8. Truncation Behaviour

The model was trained on Reddit comments, which are typically short.
The 256-token budget covers the vast majority of inputs.

When text is truncated:

- The `metadata.truncated_tokens` field is `true`.
- The model processes only the first 256 tokens (roughly the first
  400–500 words, depending on tokenisation).
- The resulting probabilities may not reflect the full emotional
  content of the text.
- The `exceeds_token_budget` method checks this without running the
  model (tokenises without truncation and compares length).

Sentimenta does **not** reject long text — it processes what fits and
flags the truncation. This is a deliberate choice: users can still get
useful results from the beginning of long text, and the metadata makes
the limitation visible.

---

## 9. Model Limitations

### Reddit Bias

The GoEmotions dataset is drawn from Reddit comments. This introduces:

- **Demographic skew**: Reddit users are disproportionately young,
  male, English-speaking, and Western.
- **Register bias**: Reddit language is informal, often uses slang,
  memes, and cultural references specific to online communities.
- **Topic bias**: Certain topics (gaming, politics, technology) are
  over-represented.

### Annotation Artifacts

- Multi-label annotation is inherently subjective. Annotators may
  disagree on which emotions apply, especially for subtle or mixed
  expressions.
- Some label pairs are frequently confused (e.g. `annoyance` vs
  `anger`, `disappointment` vs `sadness`).

### Published Performance

- Overall F1: **~0.45** under the published 0.5 threshold.
- Substantial variation across individual emotions — some (like `joy`
  and `anger`) are detected more reliably than others (like `pride`
  or `realization`).
- **Confidence scores are not certainty scores.** A 70% score for
  `excitement` means the model considers it likely but is not
  calibrated to a precise probability.

### Cultural and Demographic Limitations

- Emotional expression varies across cultures, languages, and
  demographics. The model may not generalise well to non-Western or
  non-English text.
- Sarcasm, irony, and implicit emotion are poorly handled. "Great. Just
  great." may be classified as `admiration` rather than `disapproval`.

### Explicit Disclaimer

Sentimenta displays this note with every result:

> Sentimenta provides an AI-generated interpretation of emotional
> language. Results are estimates and may not reflect the writer's
> actual feelings.

---

## 10. Derived Metrics

These are Sentimenta's presentation-layer metrics, computed from raw
model probabilities. They are **not** outputs of the GoEmotions model.

### Emotional Intensity

```
intensity = 1 - P(neutral)
```

- Range: [0, 1].
- Text dominated by neutral (P(neutral) >= 0.65) → "low" intensity.
- Text with strong emotional signal (P(neutral) <= 0.35) → "high"
  intensity.
- Intermediate → "moderate".

### Emotional Profile

The 27 non-neutral emotions are summed within each group:

- **Positive**: sum of the 12 positive-group emotion scores.
- **Negative**: sum of the 11 negative-group emotion scores.
- **Cognitive**: sum of the 4 cognitive-group emotion scores.
- **Neutral**: the single neutral label score.

Shares are normalised to sum to 1.0 so the frontend can render them as
parts of a whole (e.g. a bar chart or pie chart).

Because sigmoid outputs do not sum to 1 (multi-label), the raw group
sums can exceed 1. The normalised shares are what the UI displays.

---

## 11. Attribution: Captum Integrated Gradients

Sentimenta uses [Captum](https://captum.ai/)'s `LayerIntegratedGradients`
to identify which words contributed most toward the primary emotion.

### How It Works

1. The input is tokenised with offset mappings retained.
2. A baseline is constructed by replacing all tokens with the pad token.
3. Integrated gradients interpolates from the baseline to the actual
   input across `n_steps=16` steps (configurable via
   `SENTIMENTA_ATTRIBUTION_STEPS`).
4. The attribution is computed against the output neuron of the primary
   emotion label.
5. Per-token attributions are summed across the embedding dimension and
   aggregated from subword tokens back to words using offset mappings.
6. Adjacent words with positive attribution are merged into phrases.
7. The top 3 phrases (by attribution weight) are returned as
   `EvidenceSignal` objects with normalised weights.

### Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `enable_attribution` | `true` | Master switch. When off, explanations use probability-only summaries. |
| `attribution_steps` | `16` | Number of integration steps. Higher = more accurate but slower. |
| `attribution_max_tokens` | `128` | Maximum token length for attribution (separate from inference budget). |

### Fallback Behaviour

If attribution fails (model not loaded, tensor error, etc.), the
`ExplanationService` falls back to a probability-only explanation with
`method: "probabilities"` and an empty `signals` array. The summary
text changes to: "Token-level evidence is unavailable for this input."

---

## 12. Future Optimizations

### ONNX Runtime

Converting the PyTorch model to ONNX format and running inference via
ONNX Runtime could reduce latency by 2–3x on CPU. This is tracked in
`TODO.md` as a medium-priority item.

### INT8 Quantisation

Post-training quantisation to INT8 would reduce model size from ~500 MB
to ~125 MB and speed up inference, with a modest accuracy trade-off.
This would make deployment more accessible on resource-constrained
environments.

### Batched Attribution

Currently, attribution runs sequentially per analysis. Batching
attribution requests across multiple inputs could improve throughput
when processing sentences or concurrent requests.
