# BG0903: lane return and lane brief take agent totals silently in three cases

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_totals_said.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** US0980 QA review round 1 (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T12:59:04Z

## Summary

US0980's lane return --tokens is dropped with no word when no run is open (`record_delegated_tokens` returns None in `_lane_agent_totals`, sprint.py:8136-8165), a total for a unit outside the batch is recorded without a warning though no per-unit row shows it, and lane brief --tokens is accepted and ignored. The retro.py sibling warns in the first two cases.

## Steps to Reproduce

1. Delete the run state, then lane return --units US0101 --tokens 9000 -> rc 0, nothing said. 2. lane return --units US0199 (not in the batch) --tokens 9000 -> recorded, nothing said. 3. lane brief --units US0101 --tokens 9000 -> nothing said.

## Proposed Fix

Print one line in each case naming what was not recorded or where it went, as retro.py does.

## Acceptance Criteria

- [ ] **AC1** Given no open run, a unit outside the batch, and a lane brief, when lane return --tokens or lane brief --tokens runs in each, then each prints one line saying the total was not recorded or was recorded off the batch, and exit codes are unchanged. Fails on: the current code says nothing in all three
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_totals_said.py::LaneTotalsSaidTests::test_each_unrecorded_or_off_batch_total_is_said

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
