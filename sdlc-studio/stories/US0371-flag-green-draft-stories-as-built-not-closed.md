# US0371: flag green Draft stories as built-not-closed, forecast the unverified as new, point an all-built batch at the close path

> **Status:** Draft
> **Delivers:** CR0366
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0130
> **Points:** 5

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: Given a Draft story whose executable ACs all pass, when sprint plan selects a batch containing it

- **Given** {{context}}
- **When** {{action}}
- **Then** Given a Draft story whose executable ACs all pass, when sprint plan selects a batch containing it, then the plan flags it as built-not-closed rather than forecasting it as new work
- **Verify:** {{executable check}}

### AC2: Given a Draft story with failing or unrun ACs, when sprint plan runs, then it is forecast as

- **Given** {{context}}
- **When** {{action}}
- **Then** Given a Draft story with failing or unrun ACs, when sprint plan runs, then it is forecast as ordinary unbuilt work (the flag does not fire on unverified stories)
- **Verify:** {{executable check}}

### AC3: Given a batch where every unit is built-not-closed, when sprint plan runs, then it says so plainly

- **Given** {{context}}
- **When** {{action}}
- **Then** Given a batch where every unit is built-not-closed, when sprint plan runs, then it says so plainly and points at the close path instead of a build
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
