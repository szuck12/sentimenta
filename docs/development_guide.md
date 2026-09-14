# Development Guide

This guide covers everything needed to set up a local Sentimenta
development environment, run tests, lint, type-check, and troubleshoot
common issues.

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 22+ | Frontend runtime |
| npm | 10+ (bundled with Node) | Frontend package manager |
| git | 2.30+ | Version control |

Optional but recommended:

- **Homebrew** (macOS) for installing Python and Node.
- **pyenv** for managing Python versions.
- **nvm** for managing Node versions.

---

## Clone and Install

```bash
git clone https://github.com/<owner>/sentimenta.git
cd sentimenta

# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt   # runtime + dev tooling

# Frontend
cd frontend
npm install
cd ..
```

---

## Start the Backend

```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload
```

The API starts at `http://localhost:8000`. The model downloads
automatically on first run (~500 MB) and is cached at
`~/.cache/huggingface`.

Check readiness:

```bash
curl http://localhost:8000/api/health
# {"status":"ok","version":"1.3.3","model_loaded":true}
```

---

## Start the Frontend

```bash
cd frontend
npm run dev
```

The dev server starts at `http://localhost:5173`. The Vite config
proxies `/api` requests to the backend at `http://127.0.0.1:8000`:

```typescript
// frontend/vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    },
  },
},
```

This means the frontend can call `/api/analyze` without specifying a
base URL — Vite rewrites it to the backend automatically.

---

## Environment Variables

Copy `.env.example` to `.env` at the project root:

```bash
cp .env.example .env
```

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTIMENTA_HOST` | `127.0.0.1` | Backend bind address |
| `SENTIMENTA_PORT` | `8000` | Backend port |
| `SENTIMENTA_LOG_LEVEL` | `INFO` | Logging level |
| `SENTIMENTA_MAX_TEXT_CHARS` | `2000` | Maximum input length |
| `SENTIMENTA_MODEL_ID` | `SamLowe/roberta-base-go_emotions` | Hugging Face model |
| `SENTIMENTA_MODEL_REVISION` | pinned commit | Immutable model commit (supply-chain integrity) |
| `SENTIMENTA_MODEL_SHA256` | pinned digest | SHA-256 of the weights, verified on load |
| `SENTIMENTA_DEVICE` | (auto) | `cpu`, `mps`, or empty for auto |
| `SENTIMENTA_EMOTION_THRESHOLD` | `0.30` | Detection threshold |
| `SENTIMENTA_SENTENCE_LIMIT` | `10` | Max sentences per analysis |
| `SENTIMENTA_ENABLE_ATTRIBUTION` | `true` | Captum attribution switch |
| `SENTIMENTA_ATTRIBUTION_STEPS` | `16` | Integrated gradient steps |
| `SENTIMENTA_ENABLE_DOCS` | `false` | Expose `/docs`, `/redoc`, `/openapi.json` |
| `SENTIMENTA_RATE_LIMIT` | `30/minute` | Per-client rate limit (`0` disables) |
| `SENTIMENTA_TRUST_PROXY` | `false` | Use `X-Forwarded-For`/`X-Real-IP` for the client IP |
| `SENTIMENTA_MAX_BODY_BYTES` | `65536` | Reject larger request bodies (HTTP 413) |
| `SENTIMENTA_MAX_CONCURRENT_REQUESTS` | `4` | Concurrent analysis requests before queueing |
| `SENTIMENTA_MAX_QUEUE_WAIT_SECONDS` | `5.0` | Wait for a slot before returning HTTP 503 |

Settings are read with the `SENTIMENTA_` prefix via `pydantic-settings`.
The backend reads a `.env` file at the project root if present.

---

## Running Tests

### Backend Fast Tests (unit, API, services)

```bash
cd backend
../.venv/bin/pytest tests/unit tests/api tests/services -v
```

Unit tests cover preprocessing, metrics, the emotion taxonomy, settings,
the error envelope, and the schemas. API tests exercise HTTP
request/response round-trips with stub services. Service tests cover
analysis orchestration and the explanation fallbacks. None of these
import PyTorch or touch the network.

### Backend Model Tests

```bash
cd backend
../.venv/bin/pytest tests/model/ -v --runmodel
```

Real inference tests. Requires the downloaded model weights (~500 MB,
cached under `~/.cache/huggingface/`). Marked with `pytest.mark.model`
and skipped automatically unless `--runmodel` is passed (implemented in
`backend/conftest.py`).

### Coverage

```bash
cd backend
../.venv/bin/pytest tests/unit tests/api tests/services \
  --cov=app --cov-report=term-missing --cov-fail-under=85
```

The gate measures the `app` package and excludes the Hugging Face
wrapper (`app/services/emotion_model_service.py`), which is exercised
only by the gated model tests.

### Frontend Component Tests

```bash
cd frontend
npm run test            # single run
npm run test:watch      # watch mode
npm run test:coverage   # with an 80% coverage gate
```

Uses Vitest with jsdom, React Testing Library, and a shared setup file
(`frontend/tests/setup.ts`).

### E2E Tests (Planned)

```bash
cd frontend
npm run build
npx playwright test
```

Requires both backend and frontend servers running.

---

## Linting

### Backend (ruff)

```bash
cd backend
../.venv/bin/ruff check .
```

Auto-fix:

```bash
../.venv/bin/ruff check . --fix
```

### Frontend (ESLint)

```bash
cd frontend
npm run lint
```

Auto-fix:

```bash
npx eslint . --fix
```

### Frontend (Prettier)

```bash
cd frontend
npx prettier --write "src/**/*.{ts,tsx,css}"
```

---

## Type Checking

### Backend (mypy)

```bash
cd backend
../.venv/bin/mypy app/ --ignore-missing-imports
```

### Frontend (TypeScript)

```bash
cd frontend
npm run typecheck
```

Runs `tsc -b` across the app and node TypeScript projects.

---

## Pre-commit Hooks

The project uses pre-commit to run linters and type checkers on staged
files:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: ruff-pre-commit       # ruff check --fix
  - repo: mirrors-mypy           # mypy (backend only)
  - repo: mirrors-eslint         # eslint (frontend only)
  - repo: mirrors-prettier       # prettier (frontend only)
```

Install:

```bash
cd backend
../.venv/bin/pre-commit install
```

The hooks run automatically on `git commit`. To run manually:

```bash
../.venv/bin/pre-commit run --all-files
```

---

## CI Overview

The GitHub Actions pipeline (`.github/workflows/`) runs:

1. **Backend job**:
   - Install Python dependencies.
   - `ruff check .`
   - `mypy app/ --ignore-missing-imports`
   - `pytest tests/unit/ tests/api/ -v`
   - `pytest tests/model/ -v --runmodel` (with Hugging Face cache)

2. **Frontend job**:
   - Install Node dependencies.
   - `npm run lint`
   - `npm run typecheck`
   - `npm run test`

3. **Model cache**: `~/.cache/huggingface` is cached between runs to
   avoid re-downloading the model.

---

## Model Download

The first time the backend starts (or model tests run), the model
weights are downloaded from Hugging Face:

- **Model**: `SamLowe/roberta-base-go_emotions`
- **Size**: ~500 MB (tokenizer + model weights)
- **Cache location**: `~/.cache/huggingface/hub/models--SamLowe--roberta-base-go_emotions/`
- **Subsequent runs**: Served from cache instantly.

To pre-download:

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
AutoTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions")
AutoModelForSequenceClassification.from_pretrained("SamLowe/roberta-base-go_emotions")
```

---

## Common Issues and Solutions

### Model download fails

**Symptom**: `RuntimeError: Failed to load emotion model`

**Cause**: No internet connection, or Hugging Face is unreachable.

**Fix**: Check network access. If behind a proxy, set
`HF_ENDPOINT=https://huggingface.co` or configure `HTTP_PROXY`.

### Port 8000 already in use

**Symptom**: `ERROR: [Errno 48] Address already in use`

**Fix**: Kill the process using the port:

```bash
lsof -ti:8000 | xargs kill -9
```

Or use a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

Remember to update `SENTIMENTA_CORS_ORIGINS` and the Vite proxy target.

### MPS not available on Intel Mac

**Symptom**: Model falls back to CPU (slower).

**Fix**: This is expected. MPS requires Apple Silicon. The backend
automatically selects CPU when MPS is unavailable.

### Frontend shows "Failed to fetch"

**Symptom**: Error banner appears immediately after clicking Analyze.

**Fix**: Ensure the backend is running on port 8000. The Vite proxy
only works in dev mode (`npm run dev`), not in production builds.

### Type errors after pulling

**Symptom**: `mypy` or `tsc` report new errors.

**Fix**: Ensure dependencies are up to date:

```bash
cd backend && ../.venv/bin/pip install -r requirements-dev.txt
cd frontend && npm install
```

### Tests fail with "model not loaded"

**Symptom**: Model tests error with `Emotion model is not loaded`.

**Fix**: Run model tests with the `--runmodel` flag, which triggers
model loading. The model must be downloaded first.
