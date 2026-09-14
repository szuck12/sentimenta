# TODO Maintenance Guide

`TODO.md` is the single source of truth for all planned and in-progress
work in Sentimenta. This document describes the lifecycle, formatting
rules, and maintenance process.

---

## File Structure

```markdown
# TODO

## In Progress

## Done

## High Priority

## Medium Priority

## Low Priority

## Ideas
```

---

## Sections

### In Progress

Work actively being developed. Items here should have an owner (if
assigned) and a target PR. Limit to 3–5 items to maintain focus.

### Done

Completed items, pruned to the most recent **10 entries**. Each entry
retains its original description and tags for historical reference.
Items older than 10 are removed (they live in `CHANGELOG.md` and git
history).

### High Priority

Important changes that should be done soon. Items here are candidates
for the next sprint or release cycle.

### Medium Priority

Should get done but are not urgent. Scheduled for upcoming releases
when capacity allows.

### Low Priority

Nice-to-haves. May be addressed during quiet periods or as part of
other work.

### Ideas

Interesting ideas not yet committed to implementation. No timeline or
assignment. Reviewed periodically — promoted to a priority tier or
removed if no longer relevant.

---

## Item Format

Every item follows this format:

```markdown
- [ ] Description of the task (#tag1, #tag2)
```

- The `- [ ]` prefix is mandatory (GitHub renders it as a checkbox).
- Description is a concise imperative sentence.
- One or more `#tag`s classify the work.

### Tags

| Tag | Scope |
|-----|-------|
| `#frontend` | React, TypeScript, Tailwind, UI components, animations |
| `#backend` | FastAPI, Pydantic, services, routes, error handling |
| `#model` | PyTorch, Hugging Face, Captum, inference, attribution |
| `#test` | Unit tests, API tests, model tests, E2E tests |
| `#docs` | Documentation files, README, guides |
| `#refactor` | Code restructuring without behavior change |
| `#infra` | CI/CD, tooling, pre-commit, GitHub Actions |
| `#accessibility` | Keyboard navigation, screen readers, ARIA, contrast |

### Examples

```markdown
- [ ] Add E2E tests with Playwright covering the full analyze flow (#test)
- [ ] Investigate ONNX Runtime + quantized model for faster inference (#model)
- [ ] Add reduced-motion media query support to animations (#frontend)
- [ ] Add axe-core accessibility tests to CI (#accessibility, #test)
```

---

## Ordering Rule

**New items are always appended at the bottom of their section.**

Do not reorder existing items when adding new ones. This keeps diffs
clean and avoids accidental movement of unrelated items.

---

## Done Pruning Rule

When an item is completed:

1. Move it from its priority section to **Done**.
2. Change `- [ ]` to `- [x]`.
3. If Done has more than **10 items**, remove the oldest entries from
   the top.

Removed Done items are preserved in git history and `CHANGELOG.md`.

---

## Lifecycle

```
Idea → Low/Medium/High Priority → In Progress → Done (pruned at 10)
  │                                                       │
  └──── may be promoted or demoted at any time ────────────┘
```

### Promotion

An Idea can be promoted directly to any priority tier when it becomes
actionable. Move the item and update its position.

### Demotion

A priority item can be demoted if priorities shift. Move it to the
appropriate lower tier.

### Removal

Items that are no longer relevant (superseded, decided against, or
out of scope) are removed entirely. They are not moved to Done —
removal is for abandoned ideas, not completed work.

---

## Relationship to CHANGELOG.md

- **TODO.md** tracks what we plan to do and what we're doing now.
- **CHANGELOG.md** tracks what has been released.

When an item from TODO.md is completed and released:

1. It is marked done in TODO.md (with `[x]`).
2. It is added to the appropriate section in CHANGELOG.md under the
   relevant version.
3. It is eventually pruned from TODO.md's Done section.

The two files serve different audiences:
- TODO.md: Contributors and maintainers.
- CHANGELOG.md: Users and release managers.

---

## Maintenance cadence

- **Weekly**: Review In Progress, promote/demote priorities as needed.
- **Per release**: Move completed items to Done, update CHANGELOG.md.
- **Monthly**: Prune Done entries older than 10. Review Ideas for
  promotion.

---

## Current TODO.md Snapshot

The following items are currently tracked (as of v1.3.3):

### High Priority

- [ ] Add E2E tests with Playwright covering the full analyze flow (#test)

### Medium Priority

- [ ] Test Captum attribution against known phrase-level expectations (#test, #model)
- [ ] Investigate ONNX Runtime + quantized model for faster inference (#model)
- [ ] Add character/word count to the SentenceAnalysis response (#backend)

### Low Priority

- [ ] Add reduced-motion media query support to animations (#frontend)
- [ ] Add axe-core accessibility tests to CI (#accessibility, #test)

### Ideas

- [ ] Radial bubble visualization as an alternative to the bar chart (#frontend)
- [ ] User-configurable emotion threshold in the UI (#frontend)
