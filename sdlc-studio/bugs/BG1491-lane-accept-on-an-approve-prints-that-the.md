# BG1491: lane accept on an APPROVE prints that the unit moved to Fixed and then that its return is blocked, when one criterion has no Verify line

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_lane.py, changelog.d/BG1491.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run fourteen (RUN-01M7GEHM), BG1479 accept, 2026-11-15.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T01:57:19Z

## Summary

In run fourteen, `sprint.py lane accept --unit BG1479` on an APPROVE printed that BG1479 moved to Fixed, then that the lane return was blocked because AC3 had no Verify line (counted unspecified). The unit was left Fixed with its lane unreturned, and nothing earlier (`batch add`, `sprint plan`) had warned that AC3 had no Verify line. The operator had to add a manual Verify line and re-run `lane return`. Related: CR0708 (`file_finding` stub criteria), BG0960 (the plan's refusal wording).

## Steps to Reproduce

1. Batch a bug with one criterion that has no Verify line.
2. Land it and record an APPROVE through `sprint.py lane accept`.
3. See it report the move to Fixed and then the blocked return.

## Proposed Fix

Check every criterion has a Verify line before moving the unit, so accept either completes or refuses with nothing moved; and have `sprint.py batch add` and `sprint plan` name a criterion with no Verify line.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In run fourteen, `sprint.py lane accept --unit BG1479` on an APPROVE printed that BG1479 moved to Fixed, then that the lane return was blocked because AC3 had...
- [ ] **AC2** The proposed fix lands, pinned by a test: Check every criterion has a Verify line before moving the unit, so accept either completes or refuses with nothing moved; and have `sprint.py batch add` and...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
