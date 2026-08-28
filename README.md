# Sentimenta

Current version: **0.1.0** — [Changelog](CHANGELOG.md)

Understand what your words are feeling.

Sentimenta is a full-stack, explainable emotion-analysis web application
powered by Google's GoEmotions dataset and the RoBERTa transformer
architecture. Enter any text and receive a multi-emotion reading with
confidence scores, evidence-based explanations, and an intuitive
emotional profile.

No paid APIs. No cloud ML services. The model runs entirely locally
inside the backend.

## Features

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
- **Sentence-level analysis** — each sentence independently analysed
  when text contains multiple sentences.
- **Emotional journey** — visualise how emotions shift across your text.
- **Full spectrum view** — all 28 emotions shown as interactive bars.
- **Responsive design** — works beautifully on mobile, tablet, and
  desktop.
- **Privacy-first** — your text is analysed and returned; nothing is
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
| Recharts | Emotion visualisations |
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
| Transformers | Model loading and tokenisation |
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
| Licence | MIT |

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

## Project Structure

```
sentimenta/
├── CHANGELOG.md              # Version history
├── LICENSE                   # MIT licence
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
│   │       └── preprocessing.py         # Text normalisation
│   ├── tests/
│   │   ├── unit/             # Fast pure-logic tests
│   │   ├── api/              # HTTP round-trip tests (stubbed model)
│   │   └── model/            # Real inference tests
│   ├── requirements.txt
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
│   │   │   └── results/      # All result visualisation cards
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
│   ├── tests/
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
pip install -r backend/requirements.txt
```

### Frontend

```bash
cd sentimenta/frontend
npm install
```

The model (~500 MB) downloads automatically from Hugging Face on first
request and is cached at `~/.cache/huggingface/`.

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

## Testing

```bash
# Backend — fast unit + API tests (no model download required)
pytest backend/tests/unit backend/tests/api -v

# Backend — real model inference tests (~10 seconds)
pytest backend/tests/model -v

# Frontend — component tests
cd frontend && npm test

# All backend tests together
pytest backend/tests/ -v
```

See [docs/testing_guide.md](docs/testing_guide.md) for the full testing
methodology.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Service liveness + model status |
| GET | `/api/emotions` | Full 28-emotion taxonomy |
| POST | `/api/analyze` | Analyse a block of text |
| POST | `/api/analyze/sentences` | Analyse each sentence independently |

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

- The GoEmotions dataset is based on **Reddit comments** and carries
  the biases of that source.
- The model reports an overall F1 of approximately **0.45** under its
  published 0.5 threshold, with substantial variation across emotions.
- **Confidence scores are not certainty scores.** A score of 0.7 does
  not mean "70% sure."
- Emotional intensity, profile groupings, and the explanation layer are
  **Sentimenta presentation metrics**, not direct model outputs.

See [docs/ml_model_guide.md](docs/ml_model_guide.md) for full details.

## Privacy

- Your text is analysed in memory and returned in the API response.
- **Nothing is persisted** — no database, no logs of text content, no
  cookies.
- The model runs locally on your machine (or server); no data leaves
  your network.
- Metadata logged by the server is limited to character/word counts
  and latency numbers.

## Development Workflow

```bash
# Install pre-commit hooks (one-time setup)
pre-commit install

# Run linters before committing
ruff check backend/app backend/tests
cd frontend && npm run lint

# Type checking
mypy backend/app --ignore-missing-imports
cd frontend && npm run typecheck
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

## Licence

MIT — see [LICENSE](LICENSE).

GoEmotions dataset © Google Research,
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
