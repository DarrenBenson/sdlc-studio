# CR-0749: sprint plan names existing tests outside a unit's Affects that exercise the code it changes, so grooming widens Affects before build

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T06:37:28Z

## Summary

In run twenty (RUN-01M7VNR0), two of seven built units blocked at hand-in on an existing test outside their Affects that pins output the unit's own criteria change: BG1536 (`test_lean_guided_personas_seed.py`, via init.py's draft check) and US1036 (`test_lean_goal_seat_prd.py`, which compares the goal brief line for line). Each cost a re-groom commit and a resumed builder. Run nineteen's retro already said to stop incomplete Affects grooming; nothing checks it. sprint plan's advisory on registry files an Affects omits covers registries, not tests.

## Impact

Every sprint's groomer and builders: a unit whose criteria change printed output blocks at hand-in when a test outside its Affects pins that output, costing a re-groom commit and a resumed builder per unit.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Proposed Fix

At plan, for each script in a unit's Affects, list the test modules outside its Affects that import or invoke it, and print them per unit as an advisory grooming list, so the groomer adds the ones the criteria will break.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Raised |
