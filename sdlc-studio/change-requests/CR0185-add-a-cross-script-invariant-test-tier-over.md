# CR-0185: Add a cross-script invariant test tier over the cascade seams

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0013](../epics/EP0013-structured-authorship-and-policy-enforcement.md)
> **Priority:** Medium
> **Type:** Enhancement
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** M

## Summary

The suite has an excellent unit tier (1160 fast, isolated, green tests, roughly one file per
script) but effectively no integration tier exercising multi-script cascades as contracts -
which is exactly where this review's real bugs live.

## Motivation

The double-telemetry defect (BG0053) survives a green suite because
`test_artifact.py:265-269` asserts `recs[-1]` fields but never the record count. The system's
correctness claims are about cascades (create -> index -> count; close -> transition ->
telemetry; CLI-vs-library allocation parity), and those seams are unguarded. An invariant tier
turns "the review found it" into "the suite finds it next time" (Sam's line: green must be
earned, and a test that cannot fail is a lie - here, tests that never look at the seam).

## Scope

**In scope**

- A small invariant-test module over one fixture repo, asserting cross-module contracts:
  - close emits exactly one telemetry record (and none on idempotent re-close);
  - `artifact new` then `reconcile detect` -> zero drift for every shipped index template;
  - `cmd_allocate == allocate_number` (CLI/library parity);
  - append lands in the master table for a multi-view index layout.
- These double as regression tests for BG0053, BG0060, BG0066 once those are fixed.

**Out of scope**

- A full end-to-end markdown-flow oracle (that is the `evals/` tier; this is deterministic
  Python invariants).
- Rewriting existing unit tests.

## Acceptance Criteria

- [ ] The invariant module exists and runs in the standard `unittest discover` pass.
- [ ] Each invariant fails against the current (pre-fix) code where a bug exists (proving it
      would have caught BG0053/BG0060/BG0066), then passes once fixed.
- [ ] The "zero drift after new" invariant runs across every shipped index template, not one.
- [ ] Runtime stays within the suite's fast budget (fixture repo, no network).

## Dependencies

| Artefact | Relationship |
| --- | --- |
| BG0053, BG0060, BG0066 | This CR provides their regression tests; sequence so the invariant lands with or just after each fix |
| CR0184 | The invariants back the TRD's corrected write-contract claims |

## Risk

Low. New tests only; the one caution is not baking the current buggy behaviour into a fixture
(write each invariant to the intended contract, confirm it currently fails).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted from RV0006 test-architecture finding |
