# BG1127: A run whose plan-time baseline is folded in as a second reading beside its open stamp reads a measured token cost of 0, so RUN-01M5EM9N's close would report no spend

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py, changelog.d/BG1127.md
> **Evidence:** US1097 QA review round 1, qa-seat-US1097-r1, at a8d00e4d: pre-existing finding, reproduced at e877a6b9 on a throwaway copy of the run state.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T15:14:03Z

## Summary

US1097's QA review (round 1, 2026-10-22), pre-existing at e877a6b9. RUN-01M5EM9N's run state holds the plan-time baseline (07:13:25Z) and the open stamp (07:13:28Z) as two readings of one session; `run_token_total` takes max minus min within the session and, with the latest reading also folded to the same moment, reports a measured cost of 0 for the live run. A close taken now would state the run spent nothing, and US1095's cost check would compare 0 against the median.

## Steps to Reproduce

Read `run_state.run_token_total` on a throwaway copy of RUN-01M5EM9N's state before any later stamp: measured 0.

## Proposed Fix

Take the run's opening reading as the earliest of baseline and open stamp and the closing reading as the latest stamp after them; a run with no reading after its opening reads not attributable with a reason, never a measured 0.

## Acceptance Criteria

- [ ] **AC1** Given a run whose baseline and open stamp are both readings of one session and no later stamp, when its total is read, then it reads not attributable with a reason, never a measured 0; given a later stamp, it reads the spend between the earliest opening reading and that stamp
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py::OpeningReadingTests::test_a_baseline_beside_the_open_stamp_never_reads_a_measured_zero

## Impact

Run three's own cost figure, the one this epic exists to measure, would read 0 at its close.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
