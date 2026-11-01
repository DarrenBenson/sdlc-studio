# BG1137: The closing-review fold's append-order tiebreak between batch rows of one date is pinned by no test

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_batch_row_append_tiebreak.py
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-31T19:41:52Z

## Summary

`sprint_report.py`'s `_verdict_entries` docstring says append order decides between batch rows, but reversing that tiebreak survives the BG0962 tests and `test_sprint_report.py`: US0593's tests use distinct dates on purpose. No open Bug or CR recorded it. Found by BG0962's round-2 QA review on 2026-10-28 as pre-existing.

## Steps to Reproduce

In a throwaway copy, reverse the append-order key in the batch-row sort of the closing-review fold, then run `test_sprint_report.py` and the BG0962 test module: all pass.

## Proposed Fix

Add a test with two batch verdict rows for one unit on the same date, in which the later-appended row must decide.

## Acceptance Criteria

- [ ] **AC1** Two batch rows for one unit dated the same day are folded so that the later-appended row decides, and the test fails when the tiebreak is reversed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_row_append_tiebreak.py
  - **Verified:** yes (2026-11-01)

## Impact

A regression that lets an earlier same-day batch verdict outrank a later one would pass the suite.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Filed |
