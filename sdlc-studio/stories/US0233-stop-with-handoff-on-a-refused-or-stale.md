# US0233: stop-with-handoff on a refused or stale plan; never execute an ungated plan

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0076
> **Points:** 3

## User Story

**As an** operator returning to a run that stopped early
**I want** every boundary stop to leave a handoff naming the cause and the cycles not run
**So that** I can resume from a written record rather than reconstruct what the loop decided while I was away

## Acceptance Criteria

### AC1: A refused plan stops the run with a handoff

- **Given** a boundary whose regenerated batch is refused by the breakdown gate (ungroomed or oversized units)
- **When** the rolling loop reaches that boundary
- **Then** the batch does not execute, a handoff is written naming the refusal and the number of cycles left unrun, and run-state closes with a non-running outcome
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k RefusedPlanHandoffTests

### AC2: No ungated plan ever executes

- **Given** any of the three boundary stop causes - a failed close gate, a strict origin-drift refusal, or a refused regenerated plan
- **When** the run stops at that boundary
- **Then** no unit of the next cycle's batch is executed, and the recorded outcome and handoff distinguish which of the three causes stopped it
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k UngatedPlanNeverExecutesTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
