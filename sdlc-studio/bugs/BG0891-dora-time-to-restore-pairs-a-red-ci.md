# BG0891: DORA time to restore pairs a red CI run with an earlier green one and reports a negative duration

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_dora_time_to_restore.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RPT0014 DORA appendix, runs 36890016236 / 36861303010 / 36898472211
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T07:27:50Z

## Summary

RPT0014's DORA appendix reads Time to restore -4h 20m from forge runs 36890016236 (failure, 16:10) and 36861303010 (success, 12:22): the success chosen precedes the failure.

## Steps to Reproduce

1. A run window holding green CI at 12:22, red at 16:10, green at 17:19. 2. `sprint_report` derives DORA -> time to restore -4h 20m.

## Proposed Fix

Pair each failure with the first success that concludes AFTER it; with none, report not restored.

## Acceptance Criteria

- [ ] **AC1** Given push-triggered CI runs green at 12:22, red at 16:10 and green at 17:19, when `sprint_report` derives Time to restore, then it reads 1h 9m from the 16:10 failure to the 17:19 success, and never a negative span. Fails on: the current code reads -4h 20m
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_dora_time_to_restore.py::TimeToRestoreTests::test_restore_pairs_a_failure_with_the_next_success
  - **Verified:** yes (2026-10-02)
- [ ] **AC2** Given a red push-triggered run with no later success in the window, when sprint_report derives Time to restore, then it reads not restored and never a duration. Fails on: the current code pairs the failure with an earlier success
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_dora_time_to_restore.py::TimeToRestoreTests::test_a_failure_with_no_later_success_reads_not_restored
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
| 2026-10-02 | qa seat (goal review) | AC2 added: the control beside AC1, so the goal cannot go green on a fixture |
