# US0634: the cost is measured over one run and reported: passes spent on test-plan review versus on code review

> **Status:** Draft
> **Delivers:** CR0525
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Epic:** EP0207
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** maintainer deciding whether to keep this ceremony
**I want** the run's review passes split into plan review and code review, counted from the two ledgers
**So that** "reviewing the test is cheaper than reviewing the code" is a number this repo measured rather than the assertion the epic opened with

## Acceptance Criteria

### AC1: the split is derived from the two verdict ledgers, never from prose

- **Given** a closed run whose units carry rows in both `plan-review-verdicts.md` and `critic-verdicts.md`
- **When** `retro.py accuracy --id <retro> --write` runs
- **Then** it writes the pass count for each phase and the rejection count within each, read from the ledgers for that run's units, so the figure cannot be typed in and cannot drift from the record it describes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::PlanVersusCodeReviewCostTests::test_the_split_is_read_from_both_ledgers
- **Caller:** `retro.py accuracy --write`, whose output the close report renders
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - reading the count from the retro's prose must turn this test red
- **Verified:** no

### AC2: a run with no plan reviews reports that state rather than a zero that reads as free

- **Given** a run predating the test-plan cutoff, so no unit has a plan-review row
- **When** the same command runs
- **Then** it reports the phase as not-in-force for that run, distinguished from a run that held plan reviews and spent nothing on them, because a bare 0 in a cost column reads as evidence the ceremony is free
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::PlanVersusCodeReviewCostTests::test_a_run_without_the_phase_is_not_reported_as_zero
- **Caller:** `retro.py accuracy --write`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - emitting 0 for an absent phase must turn this test red
- **Verified:** no

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | sdlc-studio | Groomed: criteria authored against the `retro.py accuracy` slice |
