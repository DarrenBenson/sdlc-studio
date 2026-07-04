# CR-0143: batch transitions and first-class retro/review types (deterministic-toolchain ergonomics)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

> **Re-scoped (2026-07-04) after the operator's adversarial review.** First filed as a High
> 4-in-1 claiming artifact.py had "forced hand-authoring twice in one session"; the review
> checked the index state and refuted the framing (both cited artifacts are indexed, and the
> original AC list contradicted itself - if reconcile can materialise rows from the census,
> nothing was ever forced). The two gaps that survive scrutiny are ergonomics, kept here.

Two places where the deterministic toolchain makes the operator loop do mechanical work by hand:

1. **No batch transitions.** `transition.py set` takes one id, so the operator-approved
   44-bug Fixed->Closed sweep ran as a shell loop around the tool. Each transition was still
   individually gated - the gap is ergonomic, not a correctness hole.
2. **retro and review are not artifact.py types.** `next_id` allocates RETRO/RV ids, but the
   files and their index rows are hand-authored - the one artifact class outside the
   tool-created path (RETRO0006/0007 were both hand-written this week).

## Design (settled at the sprint design rung)

- **`--ids`:** comma-separated, mutually exclusive with `--id`; loop per id with
  the existing gates; one refusal prints and continues (exit non-zero if ANY
  refused); per-id result lines, plus a summary count.
- **retro/review types:** artifact.py grows a meta-type table beside
  ARTIFACT_TYPES (they live outside the status-vocab/transition machinery by
  design); `new` renders from `templates/core/{retro,review}.md` (retro template
  new, seeded from RETRO0007's shape), allocates via next_id's existing META
  path, and appends the index row. `close`/transition explicitly refuse
  meta-types with a message naming why.

## Acceptance Criteria

- [ ] `transition.py set` accepts `--ids` (comma-separated) for a batch of same-target
      transitions; each id is individually gated and individually reported, and one refusal
      does not abort the rest
- [ ] `artifact.py` supports `retro` and `review` types (template + id + index row), retiring
      the last hand-authored artifact class
- [ ] unit tests pin both; `CHANGELOG.md` [Unreleased]

## Out of Scope

- The withdrawn indexing claims: artifact.py `indexed=False` for a test-spec was observed once
  this sprint but the current index state does not support a standing defect - re-file as a BUG
  with a clean repro if it recurs.
- `reconcile apply` materialising missing rows - dropped with the narrative that motivated it;
  re-propose on its own evidence if a real missing-row loop appears.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
| 2026-07-04 | claude | Re-scoped per the operator's adversarial review: High 4-in-1 -> Medium 2-item ergonomics; refuted claims moved to Out of Scope |
| 2026-07-04 | claude | Design settled: --ids loop semantics; meta-type path for retro/review outside the transition machinery |
| 2026-07-04 | claude | Delivered: --ids batch (per-id gating, continue-past-refusal, non-zero on any block); meta_new for retro/review with template render + index row; transition meta refusal. 6 tests seen RED first. Depth: functional |
