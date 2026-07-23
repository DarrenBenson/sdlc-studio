# US0386: a zero-remaining handoff states nothing carried over, non-zero unchanged, two-sided tests

> **Status:** Draft
> **Delivers:** CR0386
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0142
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: With 0 remaining items the line states that nothing carried over and offers no --worklist command

- **Given** {{context}}
- **When** {{action}}
- **Then** With 0 remaining items the line states that nothing carried over and offers no --worklist command
- **Verify:** {{executable check}}

### AC2: With 1 or more remaining items the existing line is unchanged, naming the count and the worklist

- **Given** {{context}}
- **When** {{action}}
- **Then** With 1 or more remaining items the existing line is unchanged, naming the count and the worklist path
- **Verify:** {{executable check}}

### AC3: The boundary is pinned two-sided by tests, so a future change cannot make the zero case reappear or

- **Given** {{context}}
- **When** {{action}}
- **Then** The boundary is pinned two-sided by tests, so a future change cannot make the zero case reappear or suppress the non-zero one
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
