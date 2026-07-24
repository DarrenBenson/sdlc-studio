# US0417: the engagement floor attributes a git add -A commit to every unit it touched, not only those named

> **Status:** Draft
> **Delivers:** CR0416
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Epic:** EP0156
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: AC1: a commit touching a unit's Affects while naming a different unit is reported

- **Given** {{context}}
- **When** {{action}}
- **Then** AC1: a commit touching a unit's Affects while naming a different unit is reported
- **Verify:** {{executable check}}

### AC2: AC2: a warning, not a refusal, where ownership is ambiguous

- **Given** {{context}}
- **When** {{action}}
- **Then** AC2: a warning, not a refusal, where ownership is ambiguous
- **Verify:** {{executable check}}

### AC3: AC3: the historical mis-attribution in this repo is recorded, not silently corrected

- **Given** {{context}}
- **When** {{action}}
- **Then** AC3: the historical mis-attribution in this repo is recorded, not silently corrected
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
