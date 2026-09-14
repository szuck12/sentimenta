# Commenting Guidelines

Sentimenta is a dual-language project (Python + TypeScript). This
document defines the commenting and documentation conventions for both.

---

## 1. Python File Headers

Every Python file begins with a two-line comment identifying the file
and its purpose:

```python
# backend/app/services/metrics.py
# Derived metrics computed from raw model probabilities: threshold
# filtering, ranking, emotional intensity, and the grouped profile.
```

The first line is the relative file path. The second (and optionally
third) line is a concise description of the module's responsibility.

---

## 2. Google-Style Docstrings

All public functions, classes, and methods use Google-style docstrings:

```python
def compute_intensity(scores: dict[Emotion, float]) -> Intensity:
    """Derive the Sentimenta emotional-intensity metric.

    Defined as ``1 - P(neutral)``: emotionally flat text scores near
    zero, strongly signalled text approaches one. This is a
    Sentimenta-derived presentation metric — GoEmotions does not
    predict "intensity".

    Args:
        scores: Mapping of all labels to probabilities; must contain
            the neutral label.

    Returns:
        Intensity with both the numeric score and its band label.
    """
```

### Sections (in order)

- **One-line summary**: Imperative mood, ends with a period.
- **Extended description**: Blank line, then prose explaining the
  behavior. Use ```double backticks``` for code references.
- **Args**: Each parameter on its own line, indented, with type and
  description.
- **Returns**: Description of the return value.
- **Raises**: Exception types and when they are raised.

### When to Skip Docstrings

- Private methods with obvious behavior (`_require_loaded`, `_to_scores`)
  may have a single-line docstring or none if the name is self-documenting.
- Properties that simply return a value may omit docstrings.
- Test functions (`test_*`) never have docstrings — the function name
  IS the documentation.

---

## 3. TypeScript File Headers

Every TypeScript file begins with a two-line comment:

```typescript
// src/components/InputCard.tsx
// The primary input interface: textarea, character counter, example
// chips, clear/reset, validation messages, and the Analyze button.
```

The first line is the relative path from `src/`. The second (and
optionally third) line describes the component's or module's purpose.

---

## 4. Type Hints in Python

All function signatures must have complete type hints:

```python
def rank_emotions(
    scores: dict[Emotion, float],
) -> list[tuple[Emotion, float]]:
```

Rules:

- Use Python 3.12+ generics: `dict[K, V]`, `list[T]`, not `Dict`/`List`.
- Return types must be explicit, even for `None`:
  ```python
  def load(self) -> None:
  ```
- Use `Emotion` (the enum), not `str`, for emotion labels.
- Use `Settings` (the Pydantic model), not `dict`, for configuration.
- `# type: ignore[...]` comments are allowed only for known false
  positives (e.g. FastAPI dependency injection patterns) and must
  include the specific error code.

---

## 5. TypeScript Types

All props and return types must be explicit:

```typescript
interface SpectrumCardProps {
  emotions: EmotionPercentage[]
}

export function SpectrumCard({ emotions }: SpectrumCardProps) {
```

Rules:

- Use `interface` for component props and API responses.
- Use `type` for unions and utility types.
- No `any`. Use `unknown` if the type is truly uncertain.
- API response types in `lib/types.ts` must mirror the Pydantic schemas
  in `schemas/analysis.py`.

---

## 6. Inline Comments (Why, Not What)

Comments explain reasoning, not obvious code:

```python
# Good: explains a non-obvious threshold
# Words whose positive attribution falls below this fraction of the
# strongest word are not treated as evidence.
_SIGNAL_CUTOFF_RATIO = 0.15

# Bad: restates the code
# Filter words below the cutoff ratio
keep = [w for w in positives if w["attr"] >= peak * _SIGNAL_CUTOFF_RATIO]
```

### When Inline Comments Are Appropriate

- Explaining why a specific value was chosen.
- Documenting a non-obvious side effect.
- Clarifying a workaround for a framework limitation.
- Referencing an external source (paper, issue, documentation).

### When Inline Comments Are Not Appropriate

- Explaining what the code does (the code should be clear enough).
- Restating the function name or variable name.
- Commenting on self-evident patterns (e.g. `# iterate over items`).

---

## 7. Block Comments for ML Algorithms

ML-related code gets detailed block comments explaining the approach:

```python
# Attribution pipeline:
# 1. Tokenise with offset mappings retained.
# 2. Create baseline by replacing all tokens with pad token.
# 3. Run integrated gradients from baseline to input (n_steps=16).
# 4. Sum attributions across embedding dimension.
# 5. Aggregate subtoken attributions to words using offset mappings.
# 6. Merge adjacent words into phrases.
# 7. Return top 5 phrases by attribution weight.
```

These comments serve as algorithm documentation and are especially
important for Captum attribution, where the code involves tensor
operations that are not self-explanatory.

---

## 8. What NOT to Comment

```python
# Don't: restating imports
import torch  # import torch

# Don't: obvious assignments
self.model = model  # set the model

# Don't: TODO without context
# TODO: fix this

# Don't: outdated comments that no longer match the code
# Don't: commented-out code (use git history instead)
# Don't: decorative comments (--- separators, ASCII art)
```

---

## 9. TODO / FIXME Conventions

### Format

```python
# TODO(username): Description of what needs to be done (#tag)
# FIXME(username): Description of what is broken (#tag)
```

### Tags

| Tag | Usage |
|-----|-------|
| `#frontend` | Frontend-only work |
| `#backend` | Backend-only work |
| `#model` | ML model changes |
| `#test` | Test additions or fixes |
| `#docs` | Documentation updates |
| `#refactor` | Code restructuring |
| `#infra` | CI/CD, tooling |
| `#accessibility` | A11y improvements |

### Rules

- Every TODO must be tracked in `TODO.md` as well.
- TODOs must not be left in code without a corresponding `TODO.md`
  entry.
- FIXMEs are high-priority and must be addressed before the next
  release.
- Stale TODOs (completed or no longer relevant) must be removed.

---

## 10. Line Length

**Python**: 80 characters (ruff default). Strings and comments that
exceed this limit are wrapped to the next line with consistent
indentation.

**TypeScript**: 80 characters. Long class-name strings in CVA
definitions use string concatenation:

```typescript
const variants = cva(
  'inline-flex items-center justify-center gap-2 rounded-full '
  + 'px-6 py-3 text-sm font-semibold transition-colors '
  + 'disabled:pointer-events-none disabled:opacity-40',
)
```

---

## 11. Vertical Spacing

**Python**:

- Two blank lines between top-level function/class definitions.
- One blank line between methods within a class.
- No blank lines inside short functions (< 5 lines).
- One blank line after the module header comment block.

**TypeScript**:

- One blank line between component definitions.
- One blank line between logical sections within a component (e.g.
  between state declarations and event handlers).
- No multiple consecutive blank lines.

---

## 12. Example: Well-Commented Code

### Python

```python
# backend/app/services/metrics.py
# Derived metrics computed from raw model probabilities: threshold
# filtering, ranking, emotional intensity, and the grouped profile.

from app.core.emotions import Emotion, EmotionGroup, GROUP_MEMBERS
from app.schemas.analysis import Intensity, Profile

# Score bands for the derived intensity metric. Chosen so that a text
# dominated by neutral (P >= 0.65) reads as "low" and strongly
# signalled text (neutral <= 0.35) reads as "high".
_INTENSITY_BANDS: tuple[tuple[float, str], ...] = (
    (0.35, "low"),
    (0.65, "moderate"),
)


def rank_emotions(
    scores: dict[Emotion, float],
) -> list[tuple[Emotion, float]]:
    """Sort all 28 emotion scores from highest to lowest.

    Args:
        scores: Mapping of every GoEmotions label to its probability.

    Returns:
        (emotion, score) pairs sorted descending by score; ties break
        alphabetically by label for deterministic output.
    """
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
```

### TypeScript

```typescript
// src/components/results/SpectrumCard.tsx
// Collapsible full 28-emotion spectrum with horizontal bar chart.

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

// Emoji lookup map — one entry per GoEmotions label.
const EMOJI_MAP: Record<string, string> = {
  admiration: '👏', amusement: '😄', /* ... */
}

interface SpectrumCardProps {
  emotions: EmotionPercentage[]
}
```
