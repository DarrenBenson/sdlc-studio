# BG1335: sprint.py decision defer --block cannot mark a bug Blocked, so an autonomous run's blocked bug reads as an ordinary open unit

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_decision.py, changelog.d/BG1335.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M77177, 2026-11-12: BG1300's deferral
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:18:24Z

## Summary

`decision defer --block` sets the unit to Blocked, but Blocked is not a bug status (Open, In Progress, Fixed, Verified, Closed, Won't Fix, Superseded), so on a bug it records the decision and prints that the unit was NOT marked Blocked. The batch, status and the close then show the bug as an open unit like any other.

## Steps to Reproduce

In an open run, `sprint.py decision defer --unit BGxxxx --block --question q --option a|b --option c|d`: it prints 'unit NOT marked Blocked (\'Blocked\' is not a valid bug status ...)'.

## Proposed Fix

Record the block on the run state and surface it wherever the batch is listed, rather than writing a status the bug type lacks.

## Acceptance Criteria

- [ ] **AC1** Given an open run with a bug in its batch, when `sprint.py decision defer --unit <bug> --block` runs, then the bug is shown as blocked on the run state, in `sprint.py decision list` and in status, by a field a bug may carry. Fails on: the defer printing that it could not block and leaving the bug indistinguishable from an open unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_decision.py::DeferBlockTests::test_a_deferred_bug_is_shown_blocked

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
