# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com) and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
