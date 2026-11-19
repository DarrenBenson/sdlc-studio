# CR-0744: Amend a batch unit's Affects in flight with a recorded reason

> **Status:** Rejected
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_batch.py, changelog.d/CR0744.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** the website's RUN-01M7R7KN, 2026-11-18: orchestrator
> **Date:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T21:54:25Z

## Summary

Add an in-flight command, for example `sprint.py batch affects --unit <id> --add <path> --reason <why>`, that widens or narrows a planned unit's Affects while its run is open, records the reason with the run, and re-checks the lane partition against the other units. Today the toolchain runbook's in-flight table trades, drops and adds units and resizes the appetite, but has no row for a unit whose build finds a file it must change that it did not declare.

## Impact

On 2026-11-18 a lane in the website's run found a test outside both its units' Affects pinning the very list its criterion changes. The orchestrator hand-edited the story's Affects line on main and recorded a decision for it, which is the hand-rolling the runbook says to file. Nothing checked that the new path did not collide with a unit in another lane.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Resolution

Rejected as a duplicate of CR0656, whose US1185 (`sprint batch amend` widens a batch unit's
Affects) is this command; the website run's evidence is added to US1185.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Raised |
