# BG0926: A lane return between the close and the sign records into the run and invalidates the page before it is signed

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_closed_run_late_total.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T03:28:17Z

## Summary

BG0902 refuses a late total once a run is sealed, but a lane return --tokens made after sprint close and before sprint sign still records, so the filed page re-derives INVALIDATED and sign seals a page that no longer matches its run (reproduced at 52c1e40c and its parent by the BG0902 reviewer).

## Steps to Reproduce

1. sprint close files a page. 2. sprint lane return --units X --tokens N. 3. `sprint_report.py` check reads INVALIDATED, and sign seals it.

## Proposed Fix

Treat a run whose page is filed as closed to late totals, as a sealed run is, and say so on stderr. No new refusal beyond the existing sealed-run one.

## Acceptance Criteria

- [ ] **AC1** Given a run whose page is filed by sprint close and not yet signed, when lane return --tokens is run, then nothing is recorded, a stderr line names the closed run, and the filed page still checks VALID. Fails on: the current code, which records and invalidates the page
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_closed_run_late_total.py::ClosedRunLateTotalTests::test_a_return_after_the_close_records_nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
