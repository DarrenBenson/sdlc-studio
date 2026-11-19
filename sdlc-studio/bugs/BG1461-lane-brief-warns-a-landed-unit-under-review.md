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

Further evidence, 2026-11-19 (the website's RUN-01M7R7KN): `lane brief --units BG-01M7RJCQ` warned
that BG-01M7RAW9 and US-01M7R7HA were briefed and never returned, though both were past review:
BG-01M7RAW9 was accepted and Fixed, and US-01M7R7HA's round-two repair was landed and approved.
The two briefs it names are the round-two repair brief and the in-run bug's first brief, so the
warning outlives the review as well as the land.

## Steps to Reproduce

1. Land a lane with `sprint.py lane land --worktree <path> --units US1065`.
2. Before its review is accepted, run `sprint.py lane brief --units <another unit>`.
3. See the 'never returned' warning name US1065.

## Proposed Fix

Treat a unit `lane land` committed as returned for this warning (or word it as 'landed, awaiting review'), and keep the warning for a unit dispatched with no land and no return.

## Acceptance Criteria

- [ ] **AC1** Given a unit landed with `sprint.py lane land` and awaiting its review, when `sprint.py lane brief --units <another unit>` is run, then no warning says the landed unit never returned or tells the operator to check the diff for it. Fails on: a landed unit, whose work is committed, reported as a lane that died.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneInFlightTests::test_a_landed_unit_awaiting_review_is_not_warned_as_never_returned
- [ ] **AC2** Given a unit briefed with no land and no return, when another unit is briefed, then the 'never returned' warning still names it. Fails on: the fix silencing the warning for a lane that did die.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneInFlightTests::test_a_lane_with_no_land_and_no_return_is_still_warned

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
