# Testing Guide

Sentimenta uses a layered testing strategy that separates fast,
deterministic unit tests from slower integration tests that require real
model inference. The goal is to catch regressions early while keeping
the feedback loop short for day-to-day development.

---

## Testing Layers

| Layer | Where | Framework | Speed | External deps |
|-------|-------|-----------|-------|---------------|
| **Unit** | `backend/tests/unit/` | pytest | < 1 s | None |
| **API / Integration** | `backend/tests/api/` | pytest + httpx | < 2 s | None (stub services) |
| **Model** | `backend/tests/model/` | pytest + PyTorch | 10–30 s | Hugging Face model |
| **Component** | `frontend/tests/components/` | Vitest + RTL | < 3 s | jsdom |
| **E2E** | `tests/e2e/` | Playwright | 30–60 s | Both servers running |

---

## Backend Unit Tests

**Location**: `backend/tests/unit/`
**Runner**: `pytest`
**Dependencies**: None — pure function tests, no model, no HTTP.

### What Is Tested

#### Preprocessing (`test_preprocessing.py`)

- `normalize_text`: whitespace collapse, emoji preservation, empty string.
- `count_words`: single word, multiple words.
- `split_sentences`: simple splits, newline separation, blank paragraphs
  ignored, single sentence, long text (10 sentences), unicode
  punctuation, empty input.

#### Metrics (`test_metrics.py`)

- `rank_emotions`: descending order, tie-breaking (alphabetical).
- `detected_emotions`: threshold filtering at 0.25 and 0.90.
- `compute_intensity`: low band (neutral=0.90), moderate band
  (neutral=0.50), high band (neutral=0.05).
- `compute_profile`: shares sum to 1.0, positive-dominant,
  negative-dominant, all-zero edge case, all 28 labels present.

### Running

```bash
cd backend
../.venv/bin/pytest tests/unit/ -v
```

---

## Backend API Tests

**Location**: `backend/tests/api/`
**Runner**: `pytest` with `httpx.AsyncClient` and `ASGITransport`
**Dependencies**: None — uses `StubAnalysisService` and
`_StubModelService` injected via FastAPI dependency overrides.

### What Is Tested

- `GET /api/health` — status code, response shape, `model_loaded` is boolean.
- `GET /api/emotions` — count=28, first emotion is "admiration", correct group.
- `POST /api/analyze` — success with valid text, correct primary emotion
  label from stub scores, response shape validation.
- `POST /api/analyze` — empty text → 422 with error envelope.
- `POST /api/analyze` — text exceeding limit → 422.
- `POST /api/analyze` — malformed JSON → 422 with error envelope.
- `POST /api/analyze` — missing `text` field → 422.
- `POST /api/analyze` — wrong type for `text` (integer) → 422.
- `POST /api/analyze/sentences` — success with valid text.
- `POST /api/analyze` with `include_sentences: true` — sentences present
  in response.

### Test Infrastructure

The `conftest.py` provides:

- **`StubAnalysisService`**: Subclass of `AnalysisService` that overrides
  `analyze` and `analyze_sentences` with deterministic responses built
  from hardcoded `_STUB_SCORES`. Never imports PyTorch.
- **`_StubModelService`**: Bare object with `is_loaded = True` for
  health endpoint tests.
- **`client` fixture**: `httpx.AsyncClient` wired to a fresh FastAPI
  app with all three dependency overrides applied.

### Running

```bash
cd backend
../.venv/bin/pytest tests/api/ -v
```

---

## Backend Model Tests

**Location**: `backend/tests/model/`
**Runner**: `pytest` with `pytest.mark.model`
**Dependencies**: Real Hugging Face model (downloads ~500 MB on first run,
cached at `~/.cache/huggingface`).

### What Is Tested

All tests in `TestModelInference` and `TestSentenceAnalysis` verify:

1. **Probability range** — every score is a finite float in [0, 1].
2. **Relative ordering** — known emotional texts produce the expected
   dominant emotion (excitement text → `EXCITEMENT > SADNESS`, sadness
   text → `SADNESS > JOY`, etc.).
3. **Multi-label behaviour** — mixed-emotion text produces high scores
   for multiple labels simultaneously.
4. **All 28 labels returned** — the output contains exactly the 28
   `Emotion` enum members.
5. **Batch inference** — multiple texts processed in one call.
6. **Edge cases** — empty batch, punctuation-heavy input, emoji input,
   unicode text, empty string.
7. **Truncation** — long text (500 words) is flagged as exceeding token
   budget; short text is not.
8. **Sentence-level** — two contrasting sentences produce different
   dominant emotions.

### Corpus Fixture

The file `tests/fixtures/go_emotions_corpus.json` contains:

- **`emotion_samples`**: 28 entries, one per GoEmotions label, each
  with a representative `text` and `expected` label. Used as a reference
  for validating model behaviour against expected emotions.
- **`adversarial_samples`**: 18 entries covering sarcasm, negation,
  mixed emotions, empty input, whitespace-only, single word, emoji-only,
  punctuation-heavy, repetition, numbers, URLs, unicode, multiline,
  neutral, implicit sarcasm, ambiguous, repeated emoji, and
  multi-sentence inputs.

### Running

```bash
cd backend
../.venv/bin/pytest tests/model/ -v --runmodel
```

The `--runmodel` flag is a custom marker; check `conftest.py` or
`pyproject.toml` for its implementation. Tests in this directory are
marked with `pytestmark = pytest.mark.model` so they can be excluded
from fast test runs.

---

## Frontend Component Tests

**Location**: `frontend/tests/components/`
**Runner**: Vitest with jsdom environment
**Dependencies**: React Testing Library, `@testing-library/user-event`

### What Is Tested (`InputCard.test.tsx`)

- Renders textarea with placeholder text.
- Renders "Analyse Emotion" button.
- Displays character count.
- Shows example chips (Excitement, Neutral, etc.).
- Populates textarea on example chip click.
- Disables button when `status="loading"`.
- Shows "Start over" button when `status="success"`.

### Running

```bash
cd frontend
npm run test
```

Or in watch mode:

```bash
npm run test:watch
```

---

## E2E Tests (Planned)

**Location**: `tests/e2e/`
**Runner**: Playwright
**Dependencies**: Both backend and frontend servers running.

### Planned Test Scenarios

The 8 planned E2E test scenarios from the project spec:

1. **Happy path** — type text, click Analyse, verify primary emotion
   card renders with label and score.
2. **Example chip** — click an example chip, verify textarea populates,
   submit, verify results appear.
3. **Empty submission** — submit with no text, verify validation error.
4. **Over-limit text** — paste text exceeding 2,000 chars, verify
   character counter turns red and button is disabled.
5. **Loading state** — submit text, verify animated loading dots and
   cycling messages appear before results.
6. **Start over** — after a successful analysis, click "Start over",
   verify results clear and textarea resets.
7. **Navigation** — click "How It Works" link, verify page renders with
   the 4-step explanation. Click "Emotions" link, verify 28 emotions
   render.
8. **Sentence analysis** — submit multi-sentence text with
   `include_sentences`, verify the Emotional Journey card appears with
   per-sentence badges.

### Running (once configured)

```bash
cd frontend
npm run build
npx playwright test
```

---

## How to Add New Tests

### Backend Unit Test

1. Create or open a file in `backend/tests/unit/`.
2. Import the function under test from `app.services.*`.
3. Write functions named `test_*` with deterministic inputs.
4. Assert expected outputs. Avoid randomness or external I/O.

```python
def test_my_new_function() -> None:
    result = my_function("input")
    assert result == "expected"
```

### Backend API Test

1. Add a function to `backend/tests/api/test_routes.py`.
2. Accept the `client: httpx.AsyncClient` fixture.
3. Make a request to the endpoint.
4. Assert status code and response body.

```python
async def test_my_endpoint(client: httpx.AsyncClient) -> None:
    resp = await client.post("/api/analyze", json={"text": "hello"})
    assert resp.status_code == 200
```

### Backend Model Test

1. Add a method to `TestModelInference` or `TestSentenceAnalysis` in
   `backend/tests/model/test_emotion_model.py`.
2. Accept the `loaded_service` fixture.
3. Call `loaded_service.predict(...)` and assert relative ordering or
   probability ranges.
4. Mark the test file with `pytestmark = pytest.mark.model`.

### Frontend Component Test

1. Create or open a file in `frontend/tests/components/`.
2. Import the component and `render`/`screen` from RTL.
3. Use `userEvent` for interactions.
4. Assert DOM state.

```typescript
it('renders correctly', () => {
  render(<MyComponent />)
  expect(screen.getByText('expected text')).toBeInTheDocument()
})
```

---

## Deterministic Testing Philosophy

All fast tests (unit, API, component) must be:

- **Deterministic** — same inputs produce same outputs, every run.
- **No randomness** — no `random`, no `torch.manual_seed` needed, no
  stochastic sampling.
- **No external dependencies** — no network calls, no model downloads,
  no disk I/O beyond fixture reads.
- **No shared state** — each test function is independent; fixtures
  create fresh instances.

The model tests are the exception: they require the real Hugging Face
model and are isolated behind the `model` marker so they don't slow down
the default test run.

---

## Running All Tests

```bash
# Fast tests only (unit + API + component)
cd backend && ../.venv/bin/pytest tests/unit/ tests/api/ -v
cd frontend && npm run test

# With model inference
cd backend && ../.venv/bin/pytest tests/ -v --runmodel

# Everything (once E2E is configured)
npm run build && npx playwright test
```

---

## CI Integration

The GitHub Actions pipeline runs:

1. Backend lint (`ruff check`), type check (`mypy`), fast tests.
2. Frontend lint (`eslint`), type check (`tsc --noEmit`), component
   tests (`vitest run`).
3. Model tests in a separate job (requires model download cache).

Model test results are cached via `~/.cache/huggingface` to avoid
re-downloading ~500 MB on every run.
