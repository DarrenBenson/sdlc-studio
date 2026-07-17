# US0255: extend the write-confinement snapshot suite across the shipped writers with a roster sweep

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_confinement.py
> **Epic:** EP0082
> **Points:** 5

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: Confinement snapshots added for the major writers (artifact.py, transition.py, reconcile apply

- **Given** {{context}}
- **When** {{action}}
- **Then** Confinement snapshots added for the major writers (artifact.py, transition.py, reconcile apply, telemetry.py, retro.py, critic record, decisions.py, handoff.py, `sprint_report.py)` in SideEffectConfinementTests
- **Verify:** {{executable check}}

### AC2: A roster sweep fails when a side-effecting script has no confinement test (with an explicit

- **Given** {{context}}
- **When** {{action}}
- **Then** A roster sweep fails when a side-effecting script has no confinement test (with an explicit allowlist), or tsd.md:170 is downgraded with a Known-gap caveat matching the unit row's honesty
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
