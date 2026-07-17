# US0229: record a standing sprint policy (N cycles, goal/capacity/order/stop conditions) on run-state

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0076
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

> Seeded from the request's full criteria list - redistribute across this epic's stories as you groom them.

### AC1: sprint accepts a standing policy (N cycles + goal/capacity/order/stop conditions); each boundary

- **Given** {{context}}
- **When** {{action}}
- **Then** sprint accepts a standing policy (N cycles + goal/capacity/order/stop conditions); each boundary runs the close-down then regenerates the plan from the live backlog after a fetch
- **Verify:** {{executable check}}

### AC2: A boundary whose close gate fails, whose origin diverged under --strict, or whose regenerated plan

- **Given** {{context}}
- **When** {{action}}
- **Then** A boundary whose close gate fails, whose origin diverged under --strict, or whose regenerated plan is refused STOPS the run with a handoff - never executes a stale or ungated plan
- **Verify:** {{executable check}}

### AC3: Each cycle records its own forecast, sprint goal, retro and run-state - cycles are auditable as

- **Given** {{context}}
- **When** {{action}}
- **Then** Each cycle records its own forecast, sprint goal, retro and run-state - cycles are auditable as separate sprints
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
