# Architecture

This document describes Sentimenta's full-stack architecture, from the
browser-facing React layer through the FastAPI orchestration down to the
PyTorch inference engine.

---

## 1. Three-Layer Overview

Sentimenta is split into three logical layers:

```
┌───────────────────────────────────────────────────────────┐
│                     EXPERIENCE                            │
│  React 19 + TypeScript + Tailwind CSS + framer-motion     │
│  Pages: Home, HowIt Works, Emotions                       │
│  Components: InputCard, ResultsSection, LoadingState       │
│  UI primitives: Button, Badge, Card                       │
└───────────────────────┬───────────────────────────────────┘
                        │  HTTP / JSON
                        │  (Vite dev proxy → :8000)
┌───────────────────────▼───────────────────────────────────┐
│                     FASTAPI                               │
│  Routes: /api/health, /api/emotions,                      │
│          /api/analyze, /api/analyze/sentences              │
│  Dependency injection via module-level singletons         │
│  Error envelope standardisation                           │
└───────────┬───────────────────────────┬───────────────────┘
            │                           │
┌───────────▼───────────┐  ┌────────────▼──────────────────┐
│    INTELLIGENCE        │  │     EXPLANATION               │
│  EmotionModelService   │  │  ExplanationService           │
│  PyTorch + HF          │  │  Captum LayerIntegrated       │
│  transformers          │  │  Gradients                    │
│  RoBERTa-base          │  │  Token → word → phrase        │
│  28-label sigmoid      │  │  aggregation                  │
└────────────────────────┘  └───────────────────────────────┘
```

### Layer Responsibilities

| Layer | What it owns |
|-------|-------------|
| **Experience** | All user-facing rendering, routing, form validation, animation, responsive layout. Never touches PyTorch or model state. |
| **FastAPI** | HTTP concerns — request validation (Pydantic v2), error envelope, CORS, dependency wiring, lifespan management. |
| **Intelligence** | Model loading, tokenisation, batch inference, derived metrics (intensity, profile, ranking), sentence splitting. |
| **Explanation** | Captum attribution, subtoken-to-word aggregation, phrase detection, summary generation. |

---

## 2. Frontend Component Hierarchy

```
<App>                                          # BrowserRouter + layout shell
├── <Header>                                   # Sticky nav, hamburger menu
│   └── Nav links: Analyze, How It Works, Emotions
│
├── <Routes>
│   ├── "/" → <Home>                           # Hero + InputCard + results
│   │   ├── <InputCard>                        # Form, Zod validation, examples
│   │   ├── <LoadingState>                     # Animated dots + cycling messages
│   │   ├── <ResultsSection>                   # Staggered framer-motion container
│   │   │   ├── <PrimaryEmotionCard>           # SVG ring + emoji + confidence
│   │   │   ├── <EmotionMixCard>               # Horizontal bars for detected emotions
│   │   │   ├── <ExplanationCard>              # Summary + evidence signal pills
│   │   │   ├── <JourneyCard>                  # Vertical timeline (if sentences > 1)
│   │   │   ├── <SpectrumCard>                 # Collapsible full 28-emotion bars
│   │   │   └── Disclaimer card                # "Results are estimates" note
│   │   └── Error banner (conditional)
│   │
│   ├── "/how-it-works" → <HowItWorks>        # 4-step explanation + limitations
│   └── "/emotions" → <Emotions>              # Fetched taxonomy, grouped grid
│
└── <Footer>                                   # Privacy note, tech credits
```

### Key UI Primitives (`components/ui/`)

- **Button** — CVA-based variants: `primary` (coral), `secondary` (cream), `ghost`.
- **Badge** — Variants: `positive`, `negative`, `cognitive`, `neutral`, `default`.
- **Card** — `bg-white/80 backdrop-blur-sm border border-cream-200 shadow-sm rounded-2xl`.

### Hooks

- **`useAnalysis`** — Manages the full lifecycle: `idle → loading → success | error`. Exposes `run(text)` and `reset()`. Uses `AbortController` for in-flight cancellation.

### API Client (`lib/api.ts`)

Typed `fetch` wrapper with a generic `request<T>` function. Handles the error envelope (`{ error: { code, message } }`) and throws with the human-readable message. `BASE` is empty string; the Vite dev proxy rewrites `/api` to `localhost:8000`.

---

## 3. Backend Service Pipeline

A single analysis request flows through this pipeline:

```
HTTP Request
    │
    ▼
routes.py (validate via Pydantic schemas)
    │
    ▼
AnalysisService.analyze(text, include_sentences)
    │
    ├── preprocessing.normalize_text()
    ├── preprocessing.split_sentences()     [if include_sentences]
    │
    ├── EmotionModelService.predict()       ← batch tokenise + forward pass
    │       └── tokenizer → truncate(256) → model → sigmoid → scores
    │
    ├── metrics.rank_emotions()
    ├── metrics.detected_emotions(threshold=0.30)
    ├── metrics.compute_intensity()         ← 1 - P(neutral)
    ├── metrics.compute_profile()           ← group sums + normalised shares
    │
    ├── ExplanationService.explain()
    │       ├── predict_with_offsets()      ← retains offset_mapping
    │       ├── LayerIntegratedGradients    ← n_steps=16
    │       └── _words_to_signals()         ← subtoken → word → phrase
    │
    └── AnalyzeResponse assembled
```

### Service Ownership

| Service | File | Owns |
|---------|------|------|
| `AnalysisService` | `services/analysis_service.py` | Orchestration, metrics, sentence batching, metadata assembly |
| `EmotionModelService` | `services/emotion_model_service.py` | Model loading, tokenisation, inference, thread lock |
| `ExplanationService` | `services/explanation_service.py` | Captum attribution, phrase extraction, summary templates |
| `preprocessing` | `services/preprocessing.py` | `normalize_text`, `count_words`, `split_sentences` |
| `metrics` | `services/metrics.py` | `rank_emotions`, `detected_emotions`, `compute_intensity`, `compute_profile` |

---

## 4. Data Flow: A Single Analysis Request

1. User types text in `InputCard`, hits "Analyse Emotion".
2. `useAnalysis.run(text)` calls `api.analyze(text)`.
3. Frontend sends `POST /api/analyze { text: "...", include_sentences: false }`.
4. FastAPI validates via `AnalyzeRequest` (Pydantic v2 `Field(min_length=1, max_length=2000)`).
5. Route handler calls `AnalysisService.analyze(text, include_sentences)`.
6. `normalize_text` collapses whitespace. Empty after normalization → `EmptyTextError`.
7. `EmotionModelService.predict([normalized])` tokenises, truncates to 256 tokens, runs the model, applies sigmoid. Returns `dict[Emotion, float]` for all 28 labels.
8. `rank_emotions` sorts descending. `detected_emotions` filters at threshold 0.30.
9. `compute_intensity` returns `1 - P(neutral)` with a band label.
10. `compute_profile` sums member scores per group and normalises to shares summing to 1.
11. `ExplanationService.explain` runs Captum `LayerIntegratedGradients` against the primary emotion's output neuron, aggregates token attributions to words, merges adjacent words into phrases, and returns the top 3.
12. If `include_sentences` is true, `split_sentences` + batch `predict` produce per-sentence results (capped at `sentence_limit=10`).
13. `AnalyzeResponse` is serialised and returned. Frontend renders the results section with staggered animations.

---

## 5. Why the Model is a Singleton

The RoBERTa-base model is ~500 MB. Loading it:

- Downloads from Hugging Face cache (or fetches once on first run).
- Allocates PyTorch weights on the selected device (MPS on Apple Silicon, CPU otherwise).
- Switches to `eval()` mode.

This happens once during the FastAPI `lifespan` startup context:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    models = EmotionModelService(settings)
    models.load()                          # ← one-time cost
    explainer = ExplanationService(models, settings)
    service = AnalysisService(models, explainer, settings)
    routes._analysis_service = service     # ← injected into DI
    yield
    routes._analysis_service = None        # ← released on shutdown
```

The model instance is shared across all requests. A `threading.Lock` serialises forward passes so concurrent requests don't corrupt GPU state. This design avoids the per-request overhead of loading ~125M parameters and keeps memory usage constant regardless of traffic.

---

## 6. Why the Synthesis Layer is Separated from Inference

`AnalysisService` sits between the routes and `EmotionModelService` for three reasons:

1. **Testability** — API tests inject a `StubAnalysisService` that returns deterministic results without touching PyTorch. The model service is never imported in fast tests.

2. **Derived metrics** — GoEmotions does not output "intensity", "profile", or "grouped shares". These are computed by `metrics.py` from raw probabilities. Keeping them in a separate service makes the derivation explicit and testable independently.

3. **Sentence batching** — The `analyze` endpoint optionally re-runs the model per sentence. This logic (splitting, capping at `sentence_limit`, batch inference, per-sentence ranking) belongs in the orchestration layer, not the model wrapper.

---

## 7. Configuration Management

All settings live in `core/config.py` via `pydantic-settings`:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SENTIMENTA_", env_file=".env", extra="ignore"
    )
    max_text_chars: int = 2000
    emotion_threshold: float = 0.30
    model_id: str = "SamLowe/roberta-base-go_emotions"
    # ... etc
```

Key properties:

- **Env prefix**: `SENTIMENTA_` — all settings are overridable via environment variables (e.g. `SENTIMENTA_EMOTION_THRESHOLD=0.40`).
- **`.env` support**: The backend reads a `.env` file at the project root if present.
- **`@lru_cache` singleton**: `get_settings()` returns one `Settings` instance for the process lifetime.
- **No runtime mutation**: Settings are read-only after startup.

The `.env.example` file documents every available variable.

---

## 8. Privacy Model

Sentimenta is **stateless by design**:

- No database. No user accounts. No session persistence.
- User text is processed in-memory during the request lifecycle and never written to disk.
- No user text appears in server logs (only model IDs, character counts, and latencies are logged).
- The `Footer` component displays: "Your text is analysed and returned — nothing is stored."
- CORS origins are restricted to localhost dev ports by default.
- No API keys or secrets are required at runtime.

This architecture means the application has no data-at-rest attack surface. The only transient state is the in-flight HTTP request body and the PyTorch tensor it produces.

---

## 9. Error Envelope Standardisation

Every non-2xx response from the API uses a single envelope:

```json
{
  "error": {
    "code": "text_too_long",
    "message": "Text is 2500 characters; the limit is 2000."
  }
}
```

Three exception handlers produce this format:

| Handler | Catches | Status |
|---------|---------|--------|
| `app_error_handler` | `AppError` subclasses (`EmptyTextError`, `TextTooLongError`, `ModelUnavailableError`) | 422 or 503 |
| `validation_error_handler` | `RequestValidationError` (Pydantic failures, missing fields) | 422 |
| `unhandled_error_handler` | Any uncaught `Exception` | 500 |

The `code` field is machine-readable (e.g. `"empty_text"`, `"text_too_long"`, `"model_unavailable"`, `"invalid_request"`, `"internal_error"`). The `message` field is human-readable and safe to display to users.

`AppError` subclasses are defined in `core/errors.py`:

```python
class EmptyTextError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=422, code="empty_text",
            message="Please provide some text to analyse.",
        )
```

---

## 10. File Map

```
sentimenta/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI factory, lifespan, CORS
│   │   ├── api/routes.py              # REST endpoints + DI singletons
│   │   ├── core/
│   │   │   ├── config.py              # pydantic-settings (SENTIMENTA_ prefix)
│   │   │   ├── emotions.py            # Emotion enum, groups, emojis, descriptions
│   │   │   └── errors.py              # AppError hierarchy + handlers
│   │   ├── schemas/analysis.py        # Pydantic request/response models
│   │   └── services/
│   │       ├── analysis_service.py    # Orchestrator
│   │       ├── emotion_model_service.py  # HF model wrapper
│   │       ├── explanation_service.py # Captum attribution
│   │       ├── preprocessing.py       # Normalise, split, count
│   │       └── metrics.py            # Ranking, intensity, profile
│   └── tests/
│       ├── conftest.py                # Stub services + test client
│       ├── unit/                      # Preprocessing, metrics
│       ├── api/                       # Route tests with stubs
│       └── model/                     # Real inference tests
├── frontend/
│   ├── src/
│   │   ├── App.tsx                    # Router + layout
│   │   ├── main.tsx                   # ReactDOM entry
│   │   ├── pages/                     # Home, HowItWorks, Emotions
│   │   ├── components/
│   │   │   ├── Header.tsx, Footer.tsx, InputCard.tsx, LoadingState.tsx
│   │   │   ├── results/              # PrimaryEmotion, EmotionMix, Explanation, Spectrum, Journey
│   │   │   └── ui/                   # Button, Badge, Card
│   │   ├── hooks/useAnalysis.ts       # Analysis lifecycle hook
│   │   └── lib/
│   │       ├── api.ts                 # Typed fetch wrapper
│   │       ├── types.ts               # TypeScript interfaces (mirrors API contract)
│   │       └── utils.ts               # cn() class merger
│   └── tests/components/              # Vitest + RTL tests
├── tests/
│   ├── fixtures/go_emotions_corpus.json  # 28 emotion samples + 18 adversarial
│   ├── e2e/                           # Playwright tests (planned)
│   └── integration/                   # Cross-layer tests (planned)
├── docs/                              # This documentation
├── CHANGELOG.md
├── TODO.md
└── .env.example
```
