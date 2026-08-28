# Code Review Guide

This guide outlines the review checklist for Sentimenta pull requests.
Reviews should cover correctness, architecture adherence, security,
accessibility, and documentation consistency.

---

## 1. Conventions Compliance

### Python (Backend)

- **File headers**: Every `.py` file starts with a comment identifying
  the file path and a one-line purpose description.
  ```python
  # backend/app/services/my_service.py
  # Brief description of what this module does.
  ```
- **Docstrings**: Google-style docstrings on all public functions and
  classes. Args, Returns, and Raises sections where applicable.
- **Type hints**: All function signatures must have type hints. Return
  types must be explicit. Use `dict[Emotion, float]` (Python 3.12+
  syntax), not `Dict[Emotion, float]`.
- **Imports**: Sorted by ruff defaults. No unused imports.
- **Line length**: 80 characters (ruff default).
- **Naming**: `snake_case` for functions and variables, `PascalCase`
  for classes and enums, `UPPER_SNAKE_CASE` for constants.

### TypeScript (Frontend)

- **File headers**: Every `.tsx`/`.ts` file starts with a comment:
  ```typescript
  // src/components/MyComponent.tsx
  // Brief description of the component's purpose.
  ```
- **TypeScript strict mode**: All types must be explicit. No `any`.
  Use interfaces for object shapes, not inline types for complex objects.
- **Naming**: `PascalCase` for components and types, `camelCase` for
  functions and variables, `UPPER_SNAKE_CASE` for constants.
- **Component structure**: `forwardRef` + `displayName` for UI
  primitives. Props interfaces defined in the same file.

### Commenting

See `docs/commenting_guidelines.md` for the full standard. Key rules:

- Comments explain **why**, not **what**.
- No comments on self-explanatory code.
- ML algorithms get block comments explaining the approach.
- TODOs use the format: `# TODO(username): description (#tag)`

---

## 2. Backend Structural Audit

### Service Separation

- **AnalysisService** must orchestrate, not implement. It should call
  into `EmotionModelService`, `ExplanationService`, `preprocessing`, and
  `metrics` — not duplicate their logic.
- **EmotionModelService** must own all PyTorch/HF state. No other
  module should import `torch` or `transformers`.
- **ExplanationService** must handle attribution independently. If
  attribution fails, it falls back gracefully — never propagating
  exceptions to the route layer.
- **preprocessing** and **metrics** are pure-function modules. They
  must not import model state or settings.

### Singleton Model

- The model is loaded once in the `lifespan` context and shared via
  module-level singletons in `routes.py`.
- Tests must never load the real model in fast test runs. Use
  `StubAnalysisService` and `_StubModelService` from `conftest.py`.
- The `threading.Lock` in `EmotionModelService` serialises forward
  passes. New methods that touch `self.model` must respect this lock.

### Error Handling

- All domain errors must subclass `AppError` with a stable `code` and
  a user-safe `message`.
- New error types must be added to `core/errors.py` and handled by the
  appropriate exception handler.
- The error envelope (`{ error: { code, message } }`) must never be
  bypassed. No raw 500s with stack traces.

### Schema Consistency

- Request/response models in `schemas/analysis.py` define the API
  contract. Changes to these models are breaking changes.
- New response fields must have defaults so existing clients don't break.
- Field constraints (`min_length`, `max_length`, `ge`, `le`) must be
  documented in the field's `description`.

---

## 3. Frontend Structural Audit

### Component Composition

- UI primitives (`Button`, `Badge`, `Card`) must remain generic. No
  domain-specific logic in `components/ui/`.
- Feature components (`InputCard`, `LoadingState`) compose UI
  primitives with Sentimenta-specific logic.
- Result components (`PrimaryEmotionCard`, `EmotionMixCard`, etc.)
  receive data via props and render — they should not fetch or manage
  state.

### Hook Patterns

- `useAnalysis` manages the full analysis lifecycle. New stateful
  logic should follow the same pattern: `useState` for status, result,
  error; `useCallback` for actions; `useRef` for abort controllers.
- Hooks must not import model or service code directly. They call the
  API client (`lib/api.ts`).

### State Management

- Sentimenta uses local state only — no Redux, no Context API beyond
  React Router. Each page manages its own state.
- The `useAnalysis` hook is the single source of truth for analysis
  state on the Home page.
- The Emotions page fetches once via `useEffect` and caches in
  `useState`.

### Styling

- All styling uses Tailwind CSS utility classes. No inline styles
  except dynamic values (e.g. `style={{ width: ${pct}% }}`).
- The `cn()` utility from `lib/utils.ts` must be used for conditional
  class merging.
- Custom colors use the project's Tailwind tokens (`cream-*`, `coral-*`,
  `ink-*`, etc.), not arbitrary hex values in class names.

---

## 4. ML-Specific Review

### Model Isolation

- The model must only be accessed through `EmotionModelService`. Direct
  imports of `torch` or `transformers` outside this service are a
  review blocker.
- Attribution must only run through `ExplanationService`. Direct Captum
  usage elsewhere is not permitted.

### Threshold Documentation

- The detection threshold (0.30) is a tuning parameter, not an absolute
  boundary. Any changes to the threshold value must be documented in
  the PR description with rationale.
- The threshold is included in the response `metadata` so clients can
  interpret results. New derived metrics must similarly be transparent
  about their derivation.

### Attribution Correctness

- Captum attribution targets the primary emotion's output neuron. The
  `target_idx` must come from `model.config.label2id[target.value]`.
- Word aggregation uses offset mappings from the tokenizer. Changes to
  the tokenisation pipeline may break attribution — verify with model
  tests.
- The `_SIGNAL_CUTOFF_RATIO` (0.15) filters low-attribution words.
  Changes to this constant affect which phrases appear as evidence.

### Truncation

- Inputs exceeding 256 tokens are truncated, not rejected. The
  `truncated_tokens` flag in metadata must be set accurately.
- Attribution uses a separate budget (`attribution_max_tokens`, default
  128) to bound computational cost. Changes to either budget should be
  documented.

---

## 5. API Contract Review

### Schema Consistency

- Request and response schemas in `schemas/analysis.py` are the source
  of truth. The TypeScript types in `lib/types.ts` must mirror them.
- Adding a field to a response schema requires:
  1. A default value in the Pydantic model (so existing clients don't
     break).
  2. A corresponding TypeScript interface update in `lib/types.ts`.
  3. UI rendering of the new field (or explicit deferral tracked in
     `TODO.md`).

### Error Envelope

- All error responses must use the `{ error: { code, message } }`
  envelope. No exceptions.
- The `code` must be a stable machine-readable string. The `message`
  must be human-readable and safe to display.
- New error codes must be added to the API documentation.

### Status Codes

- `200`: Successful analysis.
- `422`: Validation failure (empty text, too long, wrong type, missing
  field).
- `503`: Model still loading.
- `500`: Unexpected error (should be rare).

---

## 6. Security Review

### Input Limits

- Text input is limited to 2,000 characters at both the Pydantic schema
  level (`Field(max_length=2000)`) and the frontend (`MAX_CHARS = 2000`).
  Both must agree.
- Sentence-level analysis is capped at 10 sentences
  (`SENTIMENTA_SENTENCE_LIMIT`).
- Attribution truncates to 128 tokens to bound computational cost.

### No Persistence

- User text must never be written to disk, logged, or stored.
- Server logs must only contain metadata (character count, latency,
  model ID), never the input text.
- The `_metadata` method in `AnalysisService` must not include user
  text in its output.

### CORS

- `cors_origins` defaults to localhost dev ports. Production
  deployments must override this to trusted domains only.
- Review any changes to `cors_origins` carefully — overly permissive
  CORS is a security risk.

### Dependencies

- Run `pip-audit` for Python dependencies and `npm audit` for Node
  dependencies periodically.
- Pin dependency versions in `requirements.txt` and `package.json`.
  Auto-updates in lockfiles should be reviewed.

---

## 7. Accessibility Review

### Keyboard Navigation

- All interactive elements must be focusable and operable via keyboard.
- Focus-visible rings (`focus-visible:ring-2 focus-visible:ring-coral-400`)
  must be present on all buttons, links, and form controls.
- The tab order must be logical (left-to-right, top-to-bottom).

### Screen Readers

- Buttons must have accessible names (either via children text or
  `aria-label`).
- Decorative emoji must be marked `aria-hidden="true"`.
- The textarea must have a `<label>` with matching `htmlFor`/`id`.
- The hamburger menu toggle must have `aria-label="Toggle navigation
  menu"`.

### Motion

- framer-motion animations should respect `prefers-reduced-motion`.
  This is tracked as a low-priority TODO.
- Loading animations (pulsing dots, cycling messages) are visual-only
  and carry no information that isn't available elsewhere.

### Color

- Text must meet WCAG AA contrast ratios against its background.
- Information must not be conveyed by color alone (e.g. badges include
  text labels, not just colored dots).

---

## 8. Documentation Consistency

### When Documentation Must Be Updated

| Change type | Files to update |
|-------------|-----------------|
| New API endpoint | `docs/api_documentation.md`, `docs/architecture.md` |
| New/changed response field | `docs/api_documentation.md`, `docs/ml_model_guide.md` |
| New emotion label or group change | `docs/emotion_taxonomy.md`, `docs/ml_model_guide.md` |
| New UI component | `docs/ui_design_guidelines.md` |
| New configuration variable | `docs/development_guide.md`, `.env.example` |
| New test layer or command | `docs/testing_guide.md` |
| New error code | `docs/api_documentation.md`, `docs/architecture.md` |
| Breaking change | `CHANGELOG.md` (under appropriate section) |

### Changelog

Every user-facing change must be reflected in `CHANGELOG.md` under the
appropriate section (Added, Changed, Fixed, Removed, Security). See
`docs/update_changelog.md` for the process.

### TODO.md

Work tracked in `TODO.md` must use the format:

```
- [ ] Description of task (#tag)
```

Tags: `#frontend`, `#backend`, `#model`, `#test`, `#docs`, `#refactor`,
`#infra`, `#accessibility`.

---

## Review Checklist

Use this checklist for every PR:

- [ ] Code follows language conventions (headers, docstrings, types)
- [ ] No direct PyTorch/HF imports outside `EmotionModelService`
- [ ] Error responses use the standard envelope
- [ ] Response schemas have defaults for new fields
- [ ] TypeScript types mirror Pydantic schemas
- [ ] Input limits enforced at both frontend and backend
- [ ] No user text in logs
- [ ] CORS changes reviewed
- [ ] New tests added for new functionality
- [ ] Documentation updated for user-facing changes
- [ ] `CHANGELOG.md` updated
- [ ] `TODO.md` updated for deferred work
- [ ] Accessibility: focus rings, aria labels, semantic HTML
- [ ] Lint and type checks pass
