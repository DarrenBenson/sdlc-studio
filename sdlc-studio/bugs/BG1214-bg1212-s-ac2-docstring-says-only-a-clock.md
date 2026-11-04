# BG1214: BG1212's AC2 docstring says only a clock can see the no-timeout join mutant, but the clock-free AC2 test also fails on it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, changelog.d/BG1214.md
> **Evidence:** BG1212 round-1 verdict, scratchpad run5/BG1212-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T17:10:34Z

## Summary

2026-11-04, BG1212's review (qa-seat-BG1212-r1, APPROVE, non-blocking). `test_meter_cursor.py`:185's docstring says the worker-joined-with-no-timeout mutant is one only a clock can see. With `worker.join()` the clock-free AC2 test also fails under the commit selection, its dribble reply reading 'its answer is not JSON' rather than the deadline (caught at :242). The cover is better than the sentence says.

## Steps to Reproduce

1. Make `worker.join(TIMEOUT_SECONDS)` `worker.join()` in `meter_cursor.py.`
2. Run the AC2 test with `-m "not boundary_only"`: it fails.

## Proposed Fix

Correct the docstring to say the clock-free test also catches it, by its reason.

## Acceptance Criteria

- [ ] **AC1** The AC2 test's docstring names what each of its mutants is caught by.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py

## Impact

A reader trusts a docstring that under-states what the test pins.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
