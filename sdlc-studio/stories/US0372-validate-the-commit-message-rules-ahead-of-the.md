# US0372: validate the commit-message rules ahead of the test lanes, no lane lost or duplicated, order pinned

> **Status:** Draft
> **Delivers:** CR0367
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0131
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: Given a commit whose message would be refused by commit-msg, when the commit is attempted, then the

- **Given** {{context}}
- **When** {{action}}
- **Then** Given a commit whose message would be refused by commit-msg, when the commit is attempted, then the message is validated BEFORE the expensive lanes run, so the refusal arrives in seconds rather than after the suite
- **Verify:** {{executable check}}

### AC2: Given a commit whose message is valid, when the commit runs, then behaviour is unchanged - the

- **Given** {{context}}
- **When** {{action}}
- **Then** Given a commit whose message is valid, when the commit runs, then behaviour is unchanged - the message check adds no new refusal, only moves an existing one earlier
- **Verify:** {{executable check}}

### AC3: Given the message check moves, when the gate runs, then no existing lane is lost or duplicated

- **Given** {{context}}
- **When** {{action}}
- **Then** Given the message check moves, when the gate runs, then no existing lane is lost or duplicated, pinned the way the lane-order reorder was pinned
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
