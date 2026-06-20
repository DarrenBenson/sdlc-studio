# CR-0033: consolidate the test-reference clique (RFC0008)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Autosprint (RFC0008)
> **RFC:** RFC-0008
> **Date:** 2026-06-20
> **Affects:** reference-test-best-practices.md, reference-test-pitfalls.md (deleted), reference-test-validation.md, SKILL.md, help/references.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Spawned from RFC0008 (Accepted, Option A + A2). The test references catalogued
anti-patterns three times (the whole `reference-test-pitfalls.md`, plus
`#common-ai-testing-mistakes` and `#test-anti-patterns` in best-practices) and two
files (`test-validation.md`, `test-pitfalls.md`) were reachable only by traversing
the clique, not from the router. Dedup the triplication into one section and expose
the orphans (A2: expose-don't-merge - lower-churn, reversible).

## Proposed Changes

1. **Dedup anti-patterns into one section.** Fold the unique content of
   `reference-test-pitfalls.md` (conditional assertions, silent helpers, the
   integration-dependency + low-coverage checklists) and the fully-subsumed
   `#common-ai-testing-mistakes` section into the single
   `reference-test-best-practices.md#test-anti-patterns`; **delete**
   `reference-test-pitfalls.md`; repoint its two See-Also references.
2. **Expose the orphans (A2).** Add Progressive Loading Guide rows (SKILL.md) for
   `reference-test-validation.md` and `reference-test-e2e-guidelines.md`, and list
   `test-validation.md` in `help/references.md`.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| reference-test-best-practices.md | one anti-patterns section (8 patterns + 2 checklists); drop subsumed section | Modified |
| reference-test-pitfalls.md | folded in and removed | Deleted |
| SKILL.md, help/references.md | router rows for the two reachable-only-via-clique files | Modified |
| reference-test-validation.md | repoint See-Also to #test-anti-patterns | Modified |

### Breaking Changes

`reference-test-pitfalls.md` is removed; its content lives at
`reference-test-best-practices.md#test-anti-patterns`. Inbound references repointed.

## Acceptance Criteria

- [x] Anti-patterns live in one `#test-anti-patterns` section; `#common-ai-testing-mistakes` (fully subsumed) and `reference-test-pitfalls.md` are gone, with no content lost (conditional assertions, silent helpers, the checklists are folded in).
- [x] No dangling references to `reference-test-pitfalls.md` or the removed anchors (anchor-link check passes).
- [x] `reference-test-validation.md` and `reference-test-e2e-guidelines.md` are reachable from the SKILL.md Progressive Loading Guide.
- [x] `npm run lint` and `npm test` pass.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0008) | Complete - dedup to one #test-anti-patterns section + delete pitfalls + router rows for the orphans |
