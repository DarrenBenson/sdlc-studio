# BG0395: The in-flight lane warning fires only for a unit re-briefed in the same command

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

The stale-marker warning is filtered to units in the current dispatch, so a lane that died on US0001 is never mentioned when the operator briefs US0002 - which is the restart case the marker exists for. Nothing else reads `lanes_in_flight`, and `close_run` leaves markers set.

## Steps to Reproduce

`record_lane_start(US0001)`; `lane brief --units US0002` -> stderr empty.

## Proposed Fix

Warn on every stale marker regardless of the briefed set, and surface them at close.

## Acceptance Criteria

- [ ] A stale in-flight marker is reported on the next brief whatever units it names.
- [ ] The close reports any unit still marked in flight.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
