# US0219: gate tracks the test-suite runtime and warns before a long run

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Epic:** EP0072
> **Depends on:** US0216
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

> Seeded from the request's full criteria list - redistribute across this epic's stories as you groom them.

### AC1: The gate records each run's test-suite wall-time to a local history of recent runs

- **Given** {{context}}
- **When** {{action}}
- **Then** The gate records each run's test-suite wall-time to a local history of recent runs, bounded to the most recent N.
- **Verify:** {{executable check}}

### AC2: Before running the suite the gate estimates duration from that history and prints a warning when it

- **Given** {{context}}
- **When** {{action}}
- **Then** Before running the suite the gate estimates duration from that history and prints a warning when it exceeds a configurable threshold (e.g. `gate.warn_seconds)`, so a long run is expected, not a surprise timeout.
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Grooming: AC3 (skip the unit suite for test-irrelevant changes) moved to its owning story US0220; `Depends on: US0216` declared |
