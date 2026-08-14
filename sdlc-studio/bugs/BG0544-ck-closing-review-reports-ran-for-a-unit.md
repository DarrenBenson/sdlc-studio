# BG0544: _ck_closing_review reports `ran` for a unit the shared coverage reading calls uncovered, when its latest sprint-level verdict is APPROVE

> **Status:** Fixed
> **Verification depth:** functional (executed: an uncovered unit carrying an APPROVE is now counted outstanding, with a covered approved unit still reporting ran as the control; mutation: 2 declared mutants, both KILLED - the first control mutant SURVIVED because it never reached the covered path, and was replaced with one that does; restore byte-exact)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07, final independent pass before the close. Reproduced by execution with `_coverage` reporting both units uncovered and an APPROVE in both ledgers.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`open_units` admits a unit the shared reading calls not-covered, but the `rejected` and `unreviewed` buckets each require a verdict test that such a unit fails - so it falls out of both, and the row returns `ran - N unit(s) approved` about a batch the shared reading says nobody covered.

Reachable through a self-reviewed sprint-review row: `_verdict_entries` reads the verdict cell without the independence check `review_coverage` applies, so a row where the reviewer is the author satisfies the fold while failing coverage.

Not a regression - at the run's base ref the row returned `ran` for any recorded review at all, so the current code is never weaker - and not close-blocking, because `sprint._close_review_coverage` is a separate first-in-chain step that refuses on `uncovered_units` using the same shared reading. What is wrong is the checklist row's prose, which is the surface an operator reads.

## Steps to Reproduce

1. Build a fixture where the shared coverage reading reports both units uncovered. 2. Record an APPROVE naming both in the sprint-review ledger. 3. Resolve the checklist. The `closing-review` row prints `ran / 2 unit(s) approved`.

## Acceptance Criteria

- [x] **AC1** Given a unit the shared coverage reading calls UNCOVERED whose latest verdict is an APPROVE, when the closing-review row renders, then it is counted outstanding - an APPROVE against a unit no independent pass covers is a verdict with nothing behind it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py -k an_uncovered_unit_with_an_approve
- [x] **AC2** Given a unit that IS covered and approved, when the same row renders, then it still reports `ran` - the fold must not swallow a genuinely reviewed unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py -k a_covered_unit_with_an_approve

## Proposed Fix

A unit that is uncovered belongs in one of the two open buckets whatever its verdict says. Fold the residue - uncovered, verdict present, verdict is an APPROVE - into `unreviewed` with its own wording, or apply the independence check in `_verdict_entries` so a self-reviewed row cannot satisfy the fold in the first place. The second is the better fix and the larger one.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in sprint_report.py `_ck_closing_review`, restore `unreviewed = [u for u in open_units if not latest.get(u)]` so the approve residue falls through | Given a unit the shared coverage reading calls UNCOVERED whose latest verdict is an APPROVE, when the closing-review row renders, then it is counted outstanding - an APPROVE against a unit no independent pass covers is a verdict with nothing behind it. |
| AC2 | in sprint_report.py `_ck_closing_review`, widen open_units to every unit so a covered approved unit stops reporting ran | Given a unit that IS covered and approved, when the same row renders, then it still reports `ran` - the fold must not swallow a genuinely reviewed unit. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
