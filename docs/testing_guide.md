# Testing Guide

Sentimenta uses a layered testing strategy that separates fast,
deterministic tests from slower integration tests that require real model
inference. The goal is to catch regressions early while keeping the
feedback loop short for day-to-day development.

---

## Testing Layers

| Layer | Where | Framework | Speed | External deps |
|-------|-------|-----------|-------|---------------|
| **Unit** | `backend/tests/unit/` | pytest | < 1 s | None |
| **API / Integration** | `backend/tests/api/` | pytest + httpx | < 1 s | None (stub services) |
| **Service** | `backend/tests/services/` | pytest | < 1 s | None (fake model) |
| **Model** | `backend/tests/model/` | pytest + PyTorch | 10–30 s | Hugging Face model, gated by `--runmodel` |
| **Component** | `frontend/tests/` | Vitest + RTL | < 10 s | jsdom |
| **E2E** | `tests/e2e/` | Playwright | 30–60 s | Both servers running (planned) |

Fast tests (unit, API, service, component) must not import PyTorch. The
model and explanation services import `torch`/`captum` lazily so that
importing the application for tests stays lightweight.

---

## Running the Suites

```bash
# Backend — fast suites
cd backend
../.venv/bin/pytest tests/unit tests/api tests/services -v

# Backend — real model inference
../.venv/bin/pytest tests/model -v --runmodel

# Backend — coverage gate
../.venv/bin/pytest tests/unit tests/api tests/services \
  --cov=app --cov-report=term-missing --cov-fail-under=85

# Frontend
cd frontend
npm run test            # single run
npm run test:watch      # watch mode
npm run test:coverage   # 80% coverage gate
```

---

## Backend Unit Tests

**Location**: `backend/tests/unit/`
**Runner**: `pytest`
**Dependencies**: None — pure function and configuration tests.

### What Is Tested

- **Preprocessing** (`test_preprocessing.py`) — whitespace collapsing,
  emoji preservation, empty input, word counting, and sentence splitting
  (punctuation, newlines, quotes, abbreviations, unicode).
- **Metrics** (`test_metrics.py`) — ranking and deterministic
  tie-breaking, threshold filtering (inclusive boundary), intensity
  bands and boundaries, and profile aggregation (shares sum to one,
  group dominance, all-zero and all-28 edge cases).
- **Taxonomy** (`test_emotions.py`) — exactly 28 unique labels, complete
  emoji/description metadata, group membership covering every label
  exactly once, and stable enum order.
- **Settings** (`test_config.py`) — defaults, environment overrides, CORS
  parsing, and `lru_cache` caching.
- **Error envelope** (`test_errors.py`) — each `AppError` subclass, the
  validation summarizer, and the sanitized 500 handler.
- **Schemas** (`test_schemas.py`) — request length bounds, probability
  bounds, attribution weight bounds, and defaults.

---

## Backend API Tests

**Location**: `backend/tests/api/`
**Runner**: `pytest` with `httpx.AsyncClient` and `ASGITransport`
**Dependencies**: None — uses `StubAnalysisService` and
`_StubModelService` injected via FastAPI dependency overrides.

### What Is Tested

- `GET /api/health` — status code, response shape, `model_loaded`.
- `GET /api/emotions` — count = 28, first label, groups, descriptions.
- `POST /api/analyze` — success, all 28 ranked emotions, metadata shape,
  empty/over-limit/missing/wrong-type input → 422, malformed JSON → 422.
- `POST /api/analyze/sentences` — success, empty text, over-limit text.
- Unknown routes → 404.
- CORS — preflight and response headers for an allowed origin.
- Error paths (`test_errors.py`) — domain errors use the envelope;
  unexpected exceptions are sanitized and never leak internals.

### Test Infrastructure

`backend/tests/conftest.py` provides:

- **`StubAnalysisService`** — deterministic responses with no PyTorch.
- **`_StubModelService`** — bare object with `is_loaded = True`.
- **`app`** — a fresh FastAPI app with all three dependencies overridden.
- **`client`** — an `httpx.AsyncClient` bound to that app.

---

## Backend Service Tests

**Location**: `backend/tests/services/`
**Runner**: `pytest`
**Dependencies**: A fake model service; no PyTorch.

- **`test_analysis_service.py`** — orchestration: primary/ranked
  emotions, threshold filtering, empty-text and model-unavailable errors,
  metadata counts/latency, truncation flag, sentence limit, and the
  attribution flag.
- **`test_explanation_service.py`** — probability fallbacks (attribution
  disabled, model not loaded, attribution raised), summary wording and
  rounding, and word/phrase aggregation from token attributions
  (merging, cutoff, zero-length offsets, top-three cap).

---

## Backend Model Tests

**Location**: `backend/tests/model/`
**Runner**: `pytest` with `pytest.mark.model`
**Dependencies**: Real Hugging Face model (~500 MB, cached at
`~/.cache/huggingface`).

Model tests are skipped unless `--runmodel` is passed. The flag is added
in `backend/conftest.py`; `pytest_collection_modifyitems` marks model
tests skipped otherwise.

### What Is Tested

- Probability range (finite, in `[0, 1]`) and all 28 labels returned.
- Relative ordering for known emotional texts and batch order.
- Multi-label behaviour and deterministic repeated inference.
- `predict_with_offsets` — scores, encoding keys, and truncation flag.
- `forward_locked` — 28-wide sigmoid output for attribution.
- Token-budget boundary consistency with the tokenizer.
- `id2label` matching the `Emotion` enum.
- Edge cases: empty string/batch, punctuation-heavy, emoji, unicode, and
  truncation of long text.

### Corpus Fixture

`tests/fixtures/go_emotions_corpus.json` contains representative and
adversarial samples used as reference material for model behaviour.

---

## Frontend Component Tests

**Location**: `frontend/tests/`
**Runner**: Vitest with jsdom
**Dependencies**: React Testing Library, `@testing-library/user-event`

Global setup (`frontend/tests/setup.ts`) loads the jest-dom matchers,
runs DOM cleanup after each test, and shims `matchMedia`,
`scrollIntoView`, and `scrollTo` for jsdom.

### What Is Tested

- **API client** (`lib/api.test.ts`) — request shaping, GET/POST paths,
  server-error messages, and network failures.
- **Utilities** (`lib/utils.test.ts`) — `cn` class merging.
- **Hook** (`hooks/useAnalysis.test.tsx`) — idle → loading →
  success/error lifecycle and reset.
- **UI primitives** (`components/ui/`) — Button, Card, Badge.
- **Feature components** — InputCard (validation, examples, counters,
  submit, reset, loading/disabled states), Header (active route, mobile
  menu), Footer, LoadingState.
- **Result cards** (`components/results/`) — PrimaryEmotionCard,
  EmotionMixCard, ExplanationCard (signals + fallback), JourneyCard
  (single-sentence guard, truncation), SpectrumCard (expand/collapse),
  and ResultsSection composition.
- **Pages and routing** — Home (submit + error), Emotions (loading +
  grouped taxonomy), HowItWorks, and App navigation.

Tests stub `fetch` with `vi.stubGlobal` and shared payloads from
`frontend/tests/fixtures.ts`.

---

## E2E Tests (Planned)

**Location**: `tests/e2e/`
**Runner**: Playwright
**Dependencies**: Both backend and frontend servers running.

Planned scenarios are listed in `tests/README.md` and the project TODO:
happy path, example chip, empty submission, over-limit text, loading
state, start over, navigation, and sentence analysis.

---

## How to Add New Tests

### Backend Unit Test

1. Create or open a file in `backend/tests/unit/`.
2. Import the function under test from `app.*`.
3. Write deterministic `test_*` functions and assert exact outputs.

### Backend API Test

1. Add a function to `backend/tests/api/`.
2. Accept the `client: httpx.AsyncClient` fixture.
3. Make a request and assert status code and body.

### Backend Service Test

1. Add a file under `backend/tests/services/`.
2. Use a fake model service (see `test_analysis_service.py`).
3. Construct the real service and assert its orchestration.

### Backend Model Test

1. Add a method to `backend/tests/model/test_emotion_model.py`.
2. Accept the `loaded_service` fixture.
3. Assert relative ordering or probability ranges. The module is already
   marked with `pytestmark = pytest.mark.model`.

### Frontend Component Test

1. Create a file under `frontend/tests/` mirroring the source path.
2. Render with RTL and interact with `userEvent`.
3. Stub `fetch` for anything that reaches the API client.

---

## Deterministic Testing Philosophy

All fast tests must be:

- **Deterministic** — same inputs, same outputs, every run.
- **Dependency-free** — no network, no model downloads, no disk I/O
  beyond fixture reads.
- **Isolated** — each test builds fresh state; no shared mutations.

The model tests are the deliberate exception and are kept behind the
`model` marker.

---

## Coverage

- **Backend**: `pytest-cov`, gated at 85% over the `app` package
  (excluding `app/services/emotion_model_service.py`).
- **Frontend**: `@vitest/coverage-v8`, gated at 80% over `src/`.

---

## CI Integration

`.github/workflows/ci.yml` runs three jobs (all with a read-only
`GITHUB_TOKEN` and commit-SHA-pinned actions):

1. **Frontend** — `npm ci`, lint, typecheck, `test:coverage`, build, then
   `npm audit --audit-level=high`.
2. **Backend** — install dev requirements, `ruff`, `mypy`, the fast suite
   with the 85% coverage gate, then `pip-audit`.
3. **Model integration** — after the backend job, run
   `pytest tests/model -v --runmodel` with the Hugging Face cache
   restored between runs.
