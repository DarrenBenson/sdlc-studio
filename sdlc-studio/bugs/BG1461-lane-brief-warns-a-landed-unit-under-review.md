# BG1461: lane brief warns a landed unit under review never returned, and that the tree may already carry its work

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run thirteen, 2026-11-15, the BG1460 lane brief.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:01:46Z

## Summary

`sprint.py lane brief --units BG1460` printed a 'was briefed ... and never returned - the working tree MAY ALREADY CARRY its work. Check the diff before starting' warning for each of six units (US1058, US1064, US1065, US1066, US1067, US1068) that had been built, landed through `lane land` (self-check recorded, QA brief written) and were waiting on review. Their work is committed on main, not loose in the tree, so the advice to check the diff is wrong for them. The warning is meant for a lane that crashed; a landed unit is reported the same way, so six false warnings bury a real one.

## Steps to Reproduce

1. Land a lane with `sprint.py lane land --worktree <path> --units US1065`.
2. Before its review is accepted, run `sprint.py lane brief --units <another unit>`.
3. See the 'never returned' warning name US1065.

## Proposed Fix

Treat a unit `lane land` committed as returned for this warning (or word it as 'landed, awaiting review'), and keep the warning for a unit dispatched with no land and no return.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint.py lane brief --units BG1460` printed a 'was briefed ...
- [ ] **AC2** The proposed fix lands, pinned by a test: Treat a unit `lane land` committed as returned for this warning (or word it as 'landed, awaiting review'), and keep the warning for a unit dispatched with no...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
