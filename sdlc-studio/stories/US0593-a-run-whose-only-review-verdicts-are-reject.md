# US0593: A run whose only review verdicts are REJECT reports the closing-review item outstanding, never ran

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0197
> **Points:** 3

## User Story

**As a** operator reading a close report
**I want** the closing-review item to read verdicts rather than count passes
**So that** four rounds of which three rejected cannot report as `ran`

## Acceptance Criteria

### AC1: REJECT-only rounds report the item outstanding

- **Given** a run whose recorded review verdicts are all REJECT
- **When** the closing-review checklist item resolves
- **Then** it is OUTSTANDING, because the item counted passes rather than reading verdicts and reported `ran` over four rounds of which three rejected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ClosingReviewVerdictTests::test_reject_only_rounds_are_outstanding

### AC2: an APPROVE covering every unit passes

- **Given** a run whose units are each covered by an APPROVE
- **When** the item resolves
- **Then** it passes - the control, so the item cannot be satisfied by one that never clears
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ClosingReviewVerdictTests::test_an_approve_covering_every_unit_passes

### AC3: a REJECT followed by a later APPROVE passes

- **Given** a unit rejected in one round and approved in a later one
- **When** the item resolves
- **Then** it passes for that unit, because a REJECT is a verdict on a revision rather than a property of the work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ClosingReviewVerdictTests::test_a_later_approve_clears_an_earlier_reject

### AC4: a partially covered run is outstanding, and names the unit nobody reviewed

- **Given** a batch of two units, one carrying an APPROVE and one carrying no verdict at all
- **When** the item resolves
- **Then** it is OUTSTANDING and names the uncovered unit, because AC2's quantifier is every
  unit and an item cleared by any single APPROVE is the same counted-passes defect one level
  down - it would report `ran` on a batch of twelve where one was reviewed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ClosingReviewVerdictTests::test_a_partially_covered_run_names_the_uncovered_unit

## Test-plan notes

Written after a plan review rejected the first draft. Three conditions the tests must meet,
recorded here because none of them fits in the plan table and each is what makes a planned
mutant lethal rather than decorative:

1. **The fixture writes its REJECTs where the counting implementation can see them** - both
   the `sprint-review-record.md` rows and the run-state review rounds. Against a fixture that
   records only per-unit `critic-verdicts.md` rows, the reverted resolver returns
   `(NOT_RUN, "none recorded")` and a test asserting OUTSTANDING passes on the broken code.
   Each test therefore asserts the row's `value` as well as its `state`: outstanding BECAUSE
   the verdicts were read must be distinguishable from outstanding because nothing was found.
2. **The per-unit fold lives in the resolver**, not in `critic.verdict_for`, which is already
   latest-wins. If the resolver delegates, AC3's mutant has no site inside this unit's declared
   `Affects` and no edit here can redden the test.
3. **AC3's two rounds carry distinct, ordered stamps.** `critic.record_verdict` writes a date
   only, so two verdicts recorded in one test tie on it and a date-keyed `max()` would pick
   either - turning the mutant into a coin toss.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | revert `_ck_closing_review` in sprint_report.py to `len(ctx['sprint_reviews'])`, reading no verdict cell | REJECT-only rounds report the item outstanding |
| AC2 | change sprint_report.py to compare the verdict cell against the spelling `APPROVED`, so a recorded APPROVE never satisfies the row | an APPROVE covering every unit passes |
| AC3 | change the per-unit fold in sprint_report.py to take `rows[0]` rather than `rows[-1]` | a REJECT followed by a later APPROVE passes |
| AC4 | change sprint_report.py to clear the row when ANY unit carries an approval rather than when every unit does | a partially covered run is outstanding, and names the unit nobody reviewed |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
