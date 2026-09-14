# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com) and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.2] - 2026-09-14

### Changed

- **Emotion Mix** now always shows the **top five emotions** with their
  percentages, instead of a varying number of threshold-detected
  emotions. Percentages are normalized with largest-remainder rounding so
  they always total exactly 100%.
- **Full Spectrum** now renders every bar in the same coral colour; the
  lighter shade for below-threshold emotions was removed.
- **Home hero copy** now reads **"What emotions does this text convey?"**
  with the subheading **"Explore the emotions and sentiment hiding inside
  text."**.

### Fixed

- **Spelling** — the loading label and error copy now use the American
  spelling **"Analyzing"** (previously "Analysing").
- **Example chips** — the "Excitement" example now produces excitement as
  the dominant emotion, and the "Worry" chip was replaced with **"Fear"**
  (worry is not a GoEmotions label) with a sentence whose primary emotion
  is fear.
- **CI backend/model jobs failed on Linux** — `pip install torch==2.14.0`
  pulled the CUDA 13 build plus the ~7 GB NVIDIA/triton dependency stack
  on Linux runners, exhausting the runner's disk during installation.
  CI now installs the CPU-only PyTorch wheel via the
  `https://download.pytorch.org/whl/cpu` index, reducing the download to
  under 200 MB with no CUDA dependencies. Local development is unchanged.

## [1.3.1] - 2026-09-13

### Added

- **Model weight integrity verification** — the downloaded safetensors
  file is checked against a pinned SHA-256 (`SENTIMENTA_MODEL_SHA256`)
  before the model is loaded.
- **Request body size limit** — requests whose declared `Content-Length`
  exceeds `SENTIMENTA_MAX_BODY_BYTES` (default 64 KB) are rejected with
  HTTP 413.
- **Concurrency cap** — analysis requests are limited to
  `SENTIMENTA_MAX_CONCURRENT_REQUESTS` (default 4); excess requests queue
  briefly and then receive HTTP 503.
- **Trusted-proxy client IP** — `SENTIMENTA_TRUST_PROXY` derives the
  client IP from `X-Forwarded-For`/`X-Real-IP` when the app runs behind a
  trusted reverse proxy.

### Changed

- **Rate limiter rewritten** — now a thread-safe, per-key sliding window
  that prunes expired timestamps and bounds memory with LRU key eviction
  (previously a single unscoped list with an O(N) scan).
- **Middleware ordering fixed** — CORS and security headers now wrap the
  rate limiter, body-size, and concurrency middleware, so 413/429/503
  responses also carry CORS and security headers, and preflight requests
  are no longer counted against the limit.
- **`SENTIMENTA_RATE_LIMIT` is validated at startup** — malformed values
  fail fast instead of silently disabling limiting.
- **`SENTIMENTA_MAX_TEXT_CHARS` is enforced by the service** in addition
  to the request schema, so lowering it actually tightens the bound.

### Removed

- **Unused `slowapi` dependency** — the custom limiter is used instead,
  removing `slowapi`, `limits`, `deprecated`, and `wrapt` from the
  runtime dependency tree.

### Security

- **Health endpoint no longer discloses `model_id`** to unauthenticated
  callers, reducing fingerprinting.

## [1.3.0] - 2026-09-13

### Added

- **In-process rate limiting** — per-IP sliding-window rate limiter on
  every endpoint (default 30 requests/minute, configurable via
  `SENTIMENTA_RATE_LIMIT`).
- **Field validation** — `attribution_steps` (0–32) and `sentence_limit`
  (1–20) are now bounded via Pydantic validators; invalid environment
  values are caught at startup.
- **CORS wildcard guard** — the `cors_origins` setting rejects `"*"`
  at validation time to prevent accidental open-origin misconfiguration.
- **Graceful error state on Emotions page** — the frontend now shows an
  error message and retry button if the emotions API call fails instead
  of showing "Loading…" indefinitely.

### Changed

- **`enable_docs` defaults to `False`** — `/docs`, `/redoc`, and
  `/openapi.json` are hidden by default in production.
- **`SENTIMENTA_HOST` defaults to `127.0.0.1`** in `.env.example`,
  with a comment explaining that containers should override to
  `0.0.0.0`.
- **CORS narrowed** — `allow_methods` and `allow_headers` restricted
  to `["GET","POST","OPTIONS"]` and `["Content-Type"]` respectively.
- **Logging respects the setting** — `basicConfig` is now applied
  inside the lifespan using the operator's `SENTIMENTA_LOG_LEVEL`.
- **Dependency guards hardened** — runtime `assert` statements in
  `routes.py` replaced with explicit `RuntimeError` raises.
- **Frontend dependencies pinned** — `react-router-dom`, `vite`,
  `vitest`, `@vitest/coverage-v8`, and `postcss` are now exact-pinned
  (no caret ranges).
- **Pre-commit prettier hook** switched from deprecated alpha mirror to
  a stable mirror (`rbubley/mirrors-prettier` v3.9.6).

### Fixed

- **Rate limiter counted unique keys instead of hits** — the sliding
  window now stores all request timestamps per key.

## [1.2.0] - 2026-09-13

### Added

- **Security hardening release** — dependency upgrades across the
  frontend and backend that clear all known advisories; both `npm audit`
  and `pip-audit` now report zero vulnerabilities.
- **Immutable model pinning** — `SENTIMENTA_MODEL_REVISION` pins the
  Hugging Face model to a specific commit, and weights load through
  safetensors only, protecting against a mutable upstream tag.
- **Security response headers** — every API response carries
  `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, and
  `Cross-Origin-Resource-Policy`.
- **`SENTIMENTA_ENABLE_DOCS`** — opt-out for `/docs`, `/redoc`, and
  `/openapi.json` so production deployments can hide the API schema.
- **CI dependency audits** — `npm audit` and `pip-audit` run in the
  pipeline, alongside least-privilege workflow permissions, commit-SHA
  pinned actions, and Dependabot coverage for GitHub Actions.
- **Expanded `.gitignore`** — ignores environment variants, key files,
  logs, and build output.

### Changed

- **Frontend toolchain upgraded** — React Router, Vite, PostCSS,
  Vitest, and the coverage provider moved to patched releases.
- **Backend runtime upgraded** — FastAPI/Starlette, Transformers,
  PyTorch, Captum, Uvicorn, and Pydantic moved to patched releases.
- **Pre-commit Prettier hook** moved from a deprecated alpha mirror to a
  stable mirror.

### Fixed

- **Tokenizer typing under Transformers 5** — the model service now
  annotates the tokenizer/model attributes explicitly so `mypy` passes.
- **Deprecated Starlette status constant** — replaced
  `HTTP_422_UNPROCESSABLE_ENTITY` with `HTTP_422_UNPROCESSABLE_CONTENT`.

## [1.1.0] - 2026-09-05

### Added

- **Expanded backend test suite** — unit tests for the emotion taxonomy,
  settings, the error envelope, and the Pydantic schemas; API tests for
  error paths, unknown routes, and CORS; service-layer orchestration tests;
  and extended real-model tests covering offset attribution and the token
  budget boundary.
- **Expanded frontend test suite** — a shared Vitest setup file plus tests
  for the API client, the `useAnalysis` hook, UI primitives, result cards,
  pages, and router navigation.
- **Coverage tooling** — `pytest-cov` for the backend and
  `@vitest/coverage-v8` for the frontend, each with a configured
  threshold.
- **`--runmodel` pytest option** — real Hugging Face inference tests are
  now skipped by default and run only when the flag is passed, matching
  the documented workflow.
- **Developer dependencies** — `backend/requirements-dev.txt` and a
  frontend ESLint flat config (`frontend/eslint.config.js`).
- **`.github/dependabot.yml`** — automated weekly pip and npm dependency
  update checks.
- **README model explainer** — expanded descriptions of the RoBERTa
  pipeline, multi-label sigmoid classification, derived metrics, and
  attribution.
- **Expanded security policy** — scope notes on model sourcing, input
  bounds, dependency scanning, container hardening, and disclosure
  handling.

### Changed

- **Version bumped to 1.1.0** across the backend settings, frontend
  package, README, and security policy.
- **Fast tests no longer import PyTorch** — `EmotionModelService` and
  `ExplanationService` now import `torch`/`captum` lazily, so the unit and
  API suites stay lightweight and quick.
- **CI workflow corrected** — fast tests, gated model tests, and
  lint/typecheck now run against the real project layout.
- **Documentation aligned** — the testing guide, development guide, and
  README now describe the commands and test inventory that actually exist.

### Fixed

- **Unimplemented `--runmodel` flag** — previously referenced by the
  README, guides, and CI but never defined, which caused real-model tests
  to run during fast test runs and would have errored CI.
- **Missing frontend ESLint configuration** — `npm run lint` and the
  pre-commit hook now have a valid flat config.
- **Broken CI test paths** — references to a non-existent
  `requirements-dev.txt` and `tests/test_model_integration.py` are gone.
- **Weak metrics test** — replaced a test that asserted nothing with a
  real 28-label profile invariant check.

## [1.0.0] - 2026-08-25

### Added

- Core emotion analysis powered by SamLowe/roberta-base-go_emotions
  (28 GoEmotions labels, multi-label sigmoid classification).
- FastAPI REST API: POST /api/analyze, POST /api/analyze/sentences,
  GET /api/emotions, GET /api/health.
- React + TypeScript frontend with Tailwind CSS, framer-motion
  animations, and responsive design.
- Evidence-based explanations via Captum integrated gradients.
- Emotional intensity metric (Sentimenta-derived, 1 - P(neutral)).
- Emotional profile grouping: positive/affiliative, negative/heavy,
  cognitive/ambiguous, neutral.
- Multi-sentence analysis with emotional journey timeline.
- Collapsible full 28-emotion spectrum visualization.
- Example texts for immediate exploration.
- Backend test suite: unit tests, API tests (stub model), real-model
  integration tests (14 edge-case and behavior tests).
- Frontend component tests with Vitest and React Testing Library.
- CI configuration (GitHub Actions).
- Project documentation: architecture, API docs, testing guide,
  ML model guide, UI design guidelines, emotion taxonomy,
  development guide, code review guide, commenting guidelines,
  changelog process, TODO maintenance guide.
