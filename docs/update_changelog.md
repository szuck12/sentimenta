# Changelog Maintenance Guide

`CHANGELOG.md` records all user-facing changes to Sentimenta, organized
by version and category. This document defines the format, rules, and
process for maintaining it.

---

## Format

The changelog follows [Keep a Changelog](https://keepachangelog.com)
and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

```markdown
# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com) and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [X.Y.Z] - YYYY-MM-DD

### Added

- Description of new feature or capability.

### Changed

- Description of a change to existing functionality.

### Fixed

- Description of a bug fix.

### Removed

- Description of removed functionality.

### Security

- Description of a security fix.
```

---

## Bump Rules (SemVer)

| Change type | Bump | Example |
|-------------|------|---------|
| Breaking change to the API contract | **MAJOR** | Removing a response field, changing a status code |
| New feature, new endpoint, new response field | **MINOR** | Adding `/api/analyze/sentences`, adding `sentences` field |
| Bug fix, docs update, test improvement, internal refactor | **PATCH** | Fixing intensity calculation, updating API docs |

### What Counts as Breaking

- Removing or renaming a response field.
- Changing a field's type.
- Changing a status code for an existing error case.
- Removing an endpoint.
- Changing the meaning of a field (e.g. `intensity.label` values).

### What Does NOT Bump Major

- Adding a new optional field with a default.
- Adding a new endpoint.
- Changing internal implementation without API surface changes.

---

## Section Definitions

### Added

New features, capabilities, or resources that didn't exist before.

Examples:
- New API endpoint.
- New UI component.
- New test layer.
- New documentation file.

### Changed

Modifications to existing functionality that are not fixes.

Examples:
- Updated model threshold from 0.5 to 0.30.
- Changed the UI color palette.
- Refactored service layer (if user-visible behavior changed).

### Fixed

Bug fixes and corrections.

Examples:
- Fixed intensity calculation when neutral probability is exactly 0.5.
- Fixed character counter not resetting on "Start over".

### Removed

Features or capabilities that were removed.

Examples:
- Removed deprecated `/api/sentiment` endpoint.

### Security

Security-related changes.

Examples:
- Updated CORS origins to restrict to production domains.
- Patched vulnerable dependency.

---

## What to Include

| Category | Include? | Section |
|----------|----------|---------|
| New feature visible to users | Yes | Added |
| New API endpoint | Yes | Added |
| New response field | Yes | Added |
| New UI component | Yes | Added |
| Changed behavior of existing feature | Yes | Changed |
| Bug fix | Yes | Fixed |
| Security fix | Yes | Security |
| New test infrastructure | Yes | Added |
| Documentation update | Yes | Added or Changed |
| Performance improvement (user-visible) | Yes | Changed |
| Internal refactoring (no behavior change) | No | — |
| Whitespace-only changes | No | — |
| Dependency bump without behavior change | No | — |
| Typo fixes in comments | No | — |
| CI configuration changes | No | — |

---

## README Update Steps

When releasing a new version, update the README alongside the
changelog:

1. **Version badge**: Update the version number in the shield badge
   at the top of README.md.

2. **Project structure**: If new files or directories were added,
   update the project structure section.

3. **Feature documentation**: If new features were added, add or update
   the relevant feature descriptions and links to documentation files.

---

## Writing Good Entries

### Do

- Write from the user's perspective, not the developer's.
- Start with a verb in imperative mood ("Add", "Fix", "Update").
- Reference the specific thing that changed.
- Include the motivation when it's not obvious.

```markdown
### Added
- Emotional journey timeline for multi-sentence analysis, showing
  per-sentence dominant emotions with group-colored badges.
```

### Don't

- Describe internal implementation details.
- Use jargon without explanation.
- Write entries that only make sense to contributors.
- Bundle multiple unrelated changes into one entry.

```markdown
### Changed
- Refactored AnalysisService to use composition over inheritance.
  (This is internal — don't include unless it changed user behavior.)
```

---

## Commit Format for Releases

When creating a release commit:

```
Release X.Y.Z — brief summary
```

Examples:

```
Release 0.1.0 — initial release with emotion analysis and explanations
Release 0.2.0 — add sentence-level emotional journey
Release 0.2.1 — fix intensity calculation for neutral-dominant text
```

---

## Versioning Process

1. Determine the bump type based on the changes since the last release.
2. Update `Settings.version` in `backend/app/core/config.py`.
3. Update the version in `frontend/package.json`.
4. Write the new section in `CHANGELOG.md` with today's date.
5. Update `README.md` version badge.
6. Commit: `Release X.Y.Z — brief summary`.
7. Tag: `git tag vX.Y.Z`.
8. Push: `git push origin main --tags`.

---

## Current Changelog

The current changelog as of v0.1.0:

```markdown
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
```
