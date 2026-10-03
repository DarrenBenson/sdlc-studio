# BG0904: DORA counts a cancelled or skipped CI run on main as a failed deployment

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_dora_cancelled_runs.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** BG0891 QA review round 1 (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T13:13:12Z

## Summary

`sprint_report._dora_rows` counts every push-triggered run whose conclusion is not success as a failure, so a cancelled or skipped run on main raises the change failure rate and opens a time-to-restore incident, and a window ending on a cancelled run reads not restored.

## Steps to Reproduce

1. A run window holding a push-triggered run concluded cancelled. 2. `sprint_report` -> change failure rate counts it and time to restore treats it as red.

## Proposed Fix

Count only conclusion failure (and `timed_out)` as a failed deployment; ignore cancelled and skipped in both figures.

## Acceptance Criteria

- [ ] **AC1** Given push-triggered runs success, cancelled, success in the window, when the page derives DORA, then the change failure rate reads 0% and time to restore reads no incident. Fails on: the current code counts the cancelled run as a failure
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_dora_cancelled_runs.py::DoraCancelledRunsTests::test_a_cancelled_run_is_not_a_failed_deployment
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
