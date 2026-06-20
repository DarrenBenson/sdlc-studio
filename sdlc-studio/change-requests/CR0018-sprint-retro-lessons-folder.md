# CR-0018: Sprint retro and committed lessons-learned folder

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Darren Benson
> **Date:** 2026-06-20
> **Affects:** reference-review.md, reference-autosprint.md, help/lessons.md, scripts/lessons.py, new sdlc-studio/retros/
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Add a **sprint retro** that, at the end of any work batch (a manual sprint, a
`review`, or an `autosprint`), writes a durable retrospective to a committed
`sdlc-studio/retros/` folder, and is read at the start of the next batch so the
loop and the operator learn. It composes with the existing two-tier `lessons.py`
(durable, generalisable lessons promote to the skill tier).

## Problem

The skill already has lessons (`lessons.py`: project tier + skill tier), but the
**project tier is `sdlc-studio/.local/lessons.md`, which is gitignored and
transient** - retrospectives are not committed, not shared, and not reliably read
at the start of the next sprint. There is no per-sprint, durable retro. And the
retro must not be autosprint-only: **not everyone uses autosprint** - a manual
sprint or a plain `review` should be able to produce and read retros too.

---

## Proposed Changes

### Item 1: Committed retros folder

**Priority:** Medium **Effort:** Low

A committed `sdlc-studio/retros/` folder with `RETRO{NNNN}-{slug}.md` artifacts
(template `templates/reviews/retro.md`): delivered, blocked, what went well, what
stalled, lessons, metrics. Plus a `retros/_index.md`.

### Item 2: Retro as a general step (not autosprint-only)

**Priority:** Medium **Effort:** Low

Add a retro step to the `review` workflow (`reference-review.md`) so any sprint or
review can write one. The `autosprint` closing gate **invokes the same capability**
rather than owning it.

### Item 3: Read retros + lessons at the start

**Priority:** Medium **Effort:** Low

`review` and `autosprint` read recent `sdlc-studio/retros/` plus `lessons recall`
(skill tier) at the start, so prior lessons enter the run. Durable, cross-project
lessons are promoted with `lessons add --global`.

---

## Impact Assessment

### Existing Functionality

Additive. Composes with `lessons.py` and `review`; no behaviour removed.

### Affected Modules

| Module | Impact | Change Type |
| --- | --- | --- |
| `sdlc-studio/retros/` | New committed folder + index | New |
| `templates/reviews/retro.md` | Retro artifact template | New (added) |
| `reference-review.md` | Optional retro step at review close | Modified |
| `reference-autosprint.md` | Closing gate invokes the retro | Modified |
| `lessons.py` / `help/lessons.md` | Promotion path documented | Modified |

### Breaking Changes

None.

---

## Acceptance Criteria

- [x] A retro can be written at the close of a `review` or an `autosprint`, to committed `sdlc-studio/retros/`.
- [x] `review`/`autosprint` read recent retros + `lessons recall` at the start.
- [x] Durable lessons promote to the skill tier via `lessons add --global`.
- [x] The capability works without autosprint (manual sprint / plain review).

## Out of Scope

- The full autosprint loop (RFC0001) - this CR is the retro capability it reuses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (determinism-sprint) | Complete - retro capability shipped (templates/reviews/retro.md, sdlc-studio/retros/, RETRO0001, start-of-sprint read in reference-autosprint.md) |
| 2026-06-20 | Darren Benson | Raised - decouple the retro/lessons-learned from autosprint so any sprint can use it |
