# BG0900: The report drops the delegated token total from the run's actual when the session meter reads zero

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_meter_zero_delegated.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** US0980 build (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T12:33:41Z

## Summary

In `sprint_report._run_tokens_actual`, when the run meter reads 0 the delegated total supplied by lane returns is dropped from the run's token actual, so a run whose orchestrator meter could not be read reports no tokens at all though agent totals were recorded.

## Steps to Reproduce

1. A run whose session meter reads 0. 2. lane return --units X --tokens 250000. 3. `sprint_report` -> the run's token actual omits the 250,000.

## Proposed Fix

Add the delegated total to the actual whatever the meter reads, and label a meter of 0 as unread rather than zero.

## Acceptance Criteria

- [ ] **AC1** Given a run whose session meter reads 0 and a lane return recording 250,000 agent tokens for unit X, when the page is derived, then the run's token actual includes the 250,000. Fails on: the current code drops it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_meter_zero_delegated.py::MeterZeroDelegatedTests::test_delegated_tokens_count_when_the_meter_reads_zero

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
