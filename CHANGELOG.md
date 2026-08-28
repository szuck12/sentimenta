# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com) and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-25

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
- Collapsible full 28-emotion spectrum visualisation.
- Example texts for immediate exploration.
- Backend test suite: unit tests, API tests (stub model), real-model
  integration tests (14 edge-case and behaviour tests).
- Frontend component tests with Vitest and React Testing Library.
- CI configuration (GitHub Actions).
- Project documentation: architecture, API docs, testing guide,
  ML model guide, UI design guidelines, emotion taxonomy,
  development guide, code review guide, commenting guidelines,
  changelog process, TODO maintenance guide.
