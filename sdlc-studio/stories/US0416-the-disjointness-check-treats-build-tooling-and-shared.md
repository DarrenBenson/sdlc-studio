# US0416: the disjointness check treats build tooling and shared config as coupling, not as ordinary files

> **Status:** Draft
> **Delivers:** CR0415
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0156
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: AC1: a unit touching build tooling is never offered as parallel-safe

- **Given** {{context}}
- **When** {{action}}
- **Then** AC1: a unit touching build tooling is never offered as parallel-safe
- **Verify:** {{executable check}}

### AC2: AC2: the set of build-tooling paths is declared, not inferred by name

- **Given** {{context}}
- **When** {{action}}
- **Then** AC2: the set of build-tooling paths is declared, not inferred by name
- **Verify:** {{executable check}}

### AC3: AC3: the contract is documented where the mode is documented

- **Given** {{context}}
- **When** {{action}}
- **Then** AC3: the contract is documented where the mode is documented
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
