# CR-0146: mutation gate v2: budget-aware sampling, dirty-tree staleness, docstring suppression

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

Three residuals logged at EP0011's close, now one coherent v2 scope - and the first is a
CORRECTNESS hole, not polish: (1) **dirty-tree staleness**: a report generated at HEAD reads
fresh across any number of uncommitted edits at the same rev (the normal pre-commit flow), so
the gate lane can render PASS on evidence about code that no longer exists - the independent
critic demonstrated it live on this repo. Content-hash staleness is the fix. (2) Ceiling
selection is naive: the dogfood run applied 12 of 2900 enumerated mutations as first-N in (file, class, line) order, so coverage clusters at the top of the alphabetically-first file; a per-file quota or prefilter-guided sampling spends the same budget far better (still deterministic - stratified by rule, never random). (3) Code-shaped lines inside docstrings/multi-line strings mutate without changing behaviour and false-survive (documented triage note today); Python's tokenizer can exclude string interiors cheaply.

## Acceptance Criteria

- [ ] the gate lane reports STALE when any target's content hash differs from the report's recorded hashes, not only on a rev change (the correctness item - lead with it)
- [ ] enumeration under a ceiling distributes the budget per file (and per class) by a documented deterministic rule; the report states the distribution
- [ ] .py enumeration skips lines inside string literals/docstrings (tokenizer-based), removing the false-survivor class
- [ ] unit tests pin all three; CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
| 2026-07-04 | claude | Operator review applied: dirty-tree staleness promoted to the leading item and named a correctness hole, not polish |
