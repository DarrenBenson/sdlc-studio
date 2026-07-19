# US0234: per-cycle auditability: own forecast, goal, retro and run-state per cycle

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0076
> **Points:** 3

## User Story

**As an** operator auditing an unattended run after the fact
**I want** each cycle to leave the same records a single sprint leaves
**So that** an N-cycle run reads as N auditable sprints rather than one blurred session

## Acceptance Criteria

### AC1: Each cycle gets its own run-state record

- **Given** a rolling run of several cycles under one policy
- **When** a cycle closes and the next one opens
- **Then** the new cycle mints a fresh `run_id` with its own `started_at` and batch, carries the cycle index and a reference to the standing policy, and the closed cycle's record stays readable rather than being overwritten
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k PerCycleRunStateTests
- **Verified:** yes (2026-07-19)

### AC2: Each cycle records its own forecast, goal and retro

- **Given** a completed rolling run of N cycles
- **When** its records are read back
- **Then** there are N forecasts, N sprint goals each with a verdict, and N retros, one set per cycle and each keyed to that cycle's `run_id`
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k PerCycleForecastGoalRetroTests
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
