# Sentimenta

Current version: **1.3.0** — [Changelog](CHANGELOG.md)

Understand what your words are feeling.

Sentimenta is a full-stack, explainable emotion-analysis web application
powered by Google's GoEmotions dataset and the RoBERTa transformer
architecture. Enter any text and receive a multi-emotion reading with
confidence scores, evidence-based explanations, and an intuitive
emotional profile.

No paid APIs. No cloud ML services. The model runs entirely locally
inside the backend.

## Features

Each request returns more than a single label: it returns a probability
for every emotion, the words that drove the strongest reading, and a set
of derived metrics that make the result easy to interpret. Highlights:

- **28 emotion labels** — not just positive/negative. Joy, anger,
  curiosity, gratitude, and 24 others.
- **Multi-label classification** — multiple emotions can score highly
  simultaneously, reflecting how real text actually feels.
- **Evidence-based explanations** — token attribution (Captum integrated
  gradients) identifies which words contributed most to the reading.
- **Emotional intensity** — a derived metric showing how emotionally
  charged your text is.
- **Emotional profile** — grouped into positive, negative, cognitive,
  and neutral families with share percentages.
- **Sentence-level analysis** — each sentence independently analyzed
  when text contains multiple sentences.
- **Emotional journey** — visualize how emotions shift across your text.
- **Full spectrum view** — all 28 emotions shown as interactive bars.
- **Responsive design** — works beautifully on mobile, tablet, and
  desktop.
- **Privacy-first** — your text is analyzed and returned; nothing is
  stored.

## Tech Stack

### Frontend

| Technology | Purpose |
|-----------|---------|
| React 19 | UI framework |
| TypeScript | Type-safe development |
| Vite 7 | Build and dev tooling |
| Tailwind CSS 3 | Styling and responsive design |
| Framer Motion | Animations and transitions |
| Recharts | Emotion visualizations |
| React Hook Form + Zod | Form management and validation |
| React Router 7 | Client-side routing |
| Vitest | Unit and component tests |

### Backend

| Technology | Purpose |
|-----------|---------|
| Python 3.12+ | Backend and ML runtime |
| FastAPI | REST API |
| Pydantic v2 | Request/response validation |
| PyTorch | Model inference |
| Transformers | Model loading and tokenization |
| Captum | Token-level attribution |
| Uvicorn | ASGI server |

### ML Model

| Component | Detail |
|-----------|--------|
| Model | SamLowe/roberta-base-go_emotions |
| Architecture | RoBERTa-base (125M params) |
| Training data | GoEmotions — 58,000 Reddit comments |
| Labels | 27 emotions + neutral (28 total) |
| Classification | Multi-label (sigmoid per emotion) |
| License | MIT |

GoEmotions is a dataset of roughly 58,000 Reddit comments, each
annotated by human raters with one or more of 27 emotion labels (or
"neutral"). `SamLowe/roberta-base-go_emotions` fine-tunes RoBERTa-base —
a 12-layer, 768-dimensional transformer encoder — on that data.

Because a comment can express several feelings at once, the model is
trained for **multi-label** classification: a sigmoid activation is
applied to each of the 28 output logits independently, so the scores are
independent probabilities rather than a distribution that sums to 1. A
comment can therefore score high for both joy and nervousness at the
same time. Sentimenta reports the highest-scoring label as the primary
emotion and lists every label at or above a tunable detection threshold
(default 0.30) as detected.

The input is truncated to a 256-token budget; longer text is still
analyzed, but the response flags `truncated_tokens: true`. Weights load
once at startup and inference runs inside the FastAPI process, so no text
ever leaves the server. The model is pinned to an immutable commit
revision and loaded through safetensors only.

## Architecture

```
                 SENTIMENTA
                     │
          ┌──────────┴──────────┐
          │                     │
      EXPERIENCE             INTELLIGENCE
          │                     │
 React / TypeScript        GoEmotions
 Tailwind CSS             RoBERTa
 Framer Motion            PyTorch
 Recharts                 Captum
 Responsive UI            Explainability
          │                     │
          └──────────┬──────────┘
                     │
                 FASTAPI
                     │
              Analysis Service
```

See [docs/architecture.md](docs/architecture.md) for the full system
design.

A request flows through five stages. The text is first normalized
(whitespace collapsed) and tokenized with the model's tokenizer,
truncated to the token budget. A single forward pass produces 28 sigmoid
probabilities. From those probabilities the service derives the
intensity metric and the grouped emotional profile, then selects the
primary emotion and any secondary emotions above the threshold. When
attribution is enabled, Captum integrated gradients runs additional
forward/backward passes against the primary emotion's output neuron and
maps sub-token attributions back to words and adjacent-word phrases. A
module-level lock serializes those passes because the model is a shared
singleton. Sentence mode repeats the scoring step per sentence, capped by
`SENTIMENTA_SENTENCE_LIMIT`.

## Project Structure

The backend separates a thin API layer (`backend/app/api`), domain
configuration and taxonomy (`core`), the public contract (`schemas`),
and the analysis pipeline (`services`). The frontend separates generic
UI primitives (`components/ui`), feature and result components
(`components`, `components/results`), the API client and shared types
(`lib`), stateful logic (`hooks`), and routed pages (`pages`).

```
sentimenta/
├── CHANGELOG.md              # Version history
├── LICENSE                   # MIT license
├── README.md                 # This file
├── SECURITY.md               # Security policy
├── TODO.md                   # Planned work
│
├── .env.example              # Environment variable template
├── .github/workflows/ci.yml  # CI pipeline
├── .gitignore
├── .pre-commit-config.yaml   # Pre-commit hooks
│
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app factory + lifespan
│   │   ├── api/routes.py     # REST endpoints
│   │   ├── core/
│   │   │   ├── config.py     # Settings (pydantic-settings)
│   │   │   ├── emotions.py   # 28-emotion taxonomy + groups
│   │   │   └── errors.py     # Error types + handlers
│   │   ├── schemas/
│   │   │   └── analysis.py   # Pydantic request/response models
│   │   └── services/
│   │       ├── analysis_service.py      # Pipeline orchestrator
│   │       ├── emotion_model_service.py # HF model singleton
│   │       ├── explanation_service.py   # Captum attribution
│   │       ├── metrics.py               # Intensity, profile
│   │       └── preprocessing.py         # Text normalization
│   ├── tests/
│   │   ├── unit/             # Pure-logic tests (metrics, taxonomy, schemas)
│   │   ├── api/              # HTTP round-trip + error tests (stub model)
│   │   ├── services/         # Orchestration + explanation fallback tests
│   │   └── model/            # Real inference tests (--runmodel)
│   ├── conftest.py           # --runmodel gate for model tests
│   ├── requirements.txt      # Runtime dependencies
│   ├── requirements-dev.txt  # Runtime + test/lint tooling
│   ├── .coveragerc           # Backend coverage configuration
│   └── pytest.ini
│
├── docs/
│   ├── architecture.md
│   ├── api_documentation.md
│   ├── code_review_guide.md
│   ├── commenting_guidelines.md
│   ├── development_guide.md
│   ├── emotion_taxonomy.md
│   ├── maintain_todo.md
│   ├── ml_model_guide.md
│   ├── testing_guide.md
│   ├── ui_design_guidelines.md
│   └── update_changelog.md
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Router + layout
│   │   ├── main.tsx          # DOM entry point
│   │   ├── index.css         # Tailwind base
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── InputCard.tsx
│   │   │   ├── LoadingState.tsx
│   │   │   ├── ui/           # Button, Card, Badge
│   │   │   └── results/      # All result visualization cards
│   │   ├── hooks/
│   │   │   └── useAnalysis.ts
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── types.ts
│   │   │   └── utils.ts
│   │   └── pages/
│   │       ├── Home.tsx
│   │       ├── HowItWorks.tsx
│   │       └── Emotions.tsx
│   ├── tests/                # Vitest + React Testing Library suites
│   ├── eslint.config.js      # ESLint 9 flat config
│   ├── vitest.config.ts      # jsdom environment + coverage gate
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
└── tests/
    ├── e2e/                  # Playwright tests (planned)
    └── fixtures/
        └── go_emotions_corpus.json
```

## Installation

### Prerequisites

- Python 3.12+
- Node.js 22+ and npm
- Git

### Backend

```bash
cd sentimenta
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Runtime dependencies only:
pip install -r backend/requirements.txt

# Or, for development (adds pytest, ruff, mypy, coverage, pip-audit):
pip install -r backend/requirements-dev.txt
```

`requirements.txt` pins the runtime (FastAPI, PyTorch, Transformers,
Captum). `requirements-dev.txt` layers the test and lint tooling on top
with pip's `-r` include, so the two never drift.

### Frontend

```bash
cd sentimenta/frontend
npm install
```

The model (~500 MB) downloads automatically from Hugging Face on first
use and is cached under `~/.cache/huggingface/`, so later runs are
offline. On Apple Silicon the backend prefers the `mps` device and falls
back to CPU automatically; set `SENTIMENTA_DEVICE=cpu` to force CPU.

## Running Locally

### Start the backend

```bash
# From the repository root
source .venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000
```

### Start the frontend

```bash
# In a second terminal
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The dev server
proxies `/api` requests to `localhost:8000`.

Start the backend first so the model can load; the first startup takes a
few seconds, or a couple of minutes on the very first run while the
weights download. The frontend dev server picks up backend changes
without a restart.

The backend reads configuration from environment variables prefixed with
`SENTIMENTA_` (see `.env.example`). The most useful knobs are
`SENTIMENTA_EMOTION_THRESHOLD` (how eager detection is),
`SENTIMENTA_ENABLE_ATTRIBUTION` (token evidence on/off),
`SENTIMENTA_ENABLE_DOCS` (hide `/docs` in production), and
`SENTIMENTA_CORS_ORIGINS` (which browser origins may call the API).

## Testing

The suite is layered so the fast tests stay fast and the real-model
tests only run when asked:

| Layer | Location | Runs by default |
|-------|----------|-----------------|
| Unit | `backend/tests/unit/` | Yes |
| API | `backend/tests/api/` | Yes |
| Services | `backend/tests/services/` | Yes |
| Model | `backend/tests/model/` | No — requires `--runmodel` |
| Components | `frontend/tests/` | Yes |

```bash
# Backend — fast suites (no PyTorch import, no model download)
cd backend
../.venv/bin/pytest tests/unit tests/api tests/services -v

# Backend — real model inference (caches ~500 MB on first run)
../.venv/bin/pytest tests/model -v --runmodel

# Backend — coverage gate (85% of app/, excluding the HF wrapper)
../.venv/bin/pytest tests/unit tests/api tests/services \
  --cov=app --cov-report=term-missing --cov-fail-under=85

# Frontend — tests, coverage, types, lint
cd frontend
npm run test
npm run test:coverage
npm run typecheck
npm run lint
```

The `--runmodel` flag is defined in `backend/conftest.py`; model-marked
tests are skipped automatically without it, keeping the default run under
a second. See [docs/testing_guide.md](docs/testing_guide.md) for the full
methodology.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Service liveness + model status |
| GET | `/api/emotions` | Full 28-emotion taxonomy |
| POST | `/api/analyze` | Analyze a block of text |
| POST | `/api/analyze/sentences` | Analyze each sentence independently |

All endpoints live under `/api`. Successful responses are JSON objects
described by the Pydantic models in `backend/app/schemas/analysis.py`.
Errors always use a single envelope, regardless of cause:

```json
{ "error": { "code": "text_too_long", "message": "Text is 2500 characters; the limit is 2000." } }
```

`POST /api/analyze` accepts up to 2,000 characters and returns the
primary emotion, all detected emotions, the full 28-label spectrum, the
derived intensity and profile, an explanation, and — optionally — one
analysis per sentence, capped by `SENTIMENTA_SENTENCE_LIMIT`. Set
`include_sentences: true` to request the sentence pass. The `metadata`
object reports character/word/sentence counts, the active threshold,
whether attribution was used, whether the input was truncated, and
per-stage latency in milliseconds.

### Example

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I cannot wait for the weekend!"}'
```

See [docs/api_documentation.md](docs/api_documentation.md) for the
complete API reference.

## Model Limitations

Sentimenta provides an AI-generated interpretation of emotional
language. Results are estimates and may not reflect the writer's actual
feelings.

Key limitations:

- The GoEmotions dataset is based on **Reddit comments** and carries the
  biases of that source. Performance varies across cultures, dialects,
  and writing styles, and short or ambiguous text may be read
  differently than a person would read it.
- The model reports an overall F1 of approximately **0.45** under its
  published 0.5 threshold, with substantial variation across emotions.
  Common labels such as neutral, joy, and gratitude are detected far
  more reliably than rare or subtle ones.
- **Confidence scores are not certainty scores.** A score of 0.7 does
  not mean "70% sure." It is an independent sigmoid value that is useful
  for ranking emotions within one input, but it is not calibrated as a
  probability of correctness.
- Emotional intensity, profile groupings, and the explanation layer are
  **Sentimenta presentation metrics**, not direct model outputs. The
  model predicts emotion probabilities; the intensity score
  (`1 − P(neutral)`), the four group shares, and the phrase-level
  evidence are all derived by Sentimenta and documented in
  [docs/ml_model_guide.md](docs/ml_model_guide.md).
- Token attribution shows which words influenced the primary emotion,
  but it does not prove causation: integrated gradients is a local
  sensitivity method and can be noisy on very short inputs.

See [docs/ml_model_guide.md](docs/ml_model_guide.md) for full details.

## Privacy

- Your text is analyzed in memory and returned in the API response.
- **Nothing is persisted** — no database, no logs of text content, no
  cookies, and no analytics. There are no accounts and therefore no user
  data to associate with a request.
- The model runs in the same process as the API (locally, or on the
  server you deploy to); no text is sent to a third-party ML service.
- Metadata logged by the server is limited to character/word counts and
  latency numbers. Verbosity is controlled by `SENTIMENTA_LOG_LEVEL`.
- Cross-origin access is restricted by an explicit allowlist
  (`SENTIMENTA_CORS_ORIGINS`); unknown browser origins are rejected.

## Development Workflow

```bash
# Install development dependencies (runtime + lint/test tooling)
pip install -r backend/requirements-dev.txt
cd frontend && npm install

# Install pre-commit hooks (one-time setup)
pre-commit install

# Lint before committing
cd backend && ruff check .
cd frontend && npm run lint

# Type checking
mypy backend/app --ignore-missing-imports
cd frontend && npm run typecheck

# Fast tests with coverage
cd backend && ../.venv/bin/pytest tests/unit tests/api tests/services --cov=app
cd frontend && npm run test:coverage
```

See [docs/development_guide.md](docs/development_guide.md) for the full
developer guide.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-change`)
3. Make changes following the code style in
   [docs/commenting_guidelines.md](docs/commenting_guidelines.md)
4. Add or update tests as needed
5. Update `CHANGELOG.md` per
   [docs/update_changelog.md](docs/update_changelog.md)
6. Submit a pull request

Before opening a PR, make sure the fast backend suite, the frontend
lint/typecheck/tests, and both coverage gates pass locally (see
[Testing](#testing)).

## License

MIT — see [LICENSE](LICENSE).

GoEmotions dataset © Google Research,
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
