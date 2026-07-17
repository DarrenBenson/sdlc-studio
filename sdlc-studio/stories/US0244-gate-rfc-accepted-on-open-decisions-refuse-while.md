# US0244: gate RFC -> Accepted on open decisions (refuse while any Open decision stands; recorded-override escape)

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/validate.py
> **Epic:** EP0079
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

> Seeded from the request's full criteria list - redistribute across this epic's stories as you groom them.

### AC1: transition.py refuses RFC -> Accepted while any Open Decision row is Open, with a recorded-override

- **Given** {{context}}
- **When** {{action}}
- **Then** transition.py refuses RFC -> Accepted while any Open Decision row is Open, with a recorded-override escape consistent with the gate doctrine
- **Verify:** {{executable check}}

### AC2: `file_finding.py`'s RFC template derives decision rows from the finding's real options instead of

- **Given** {{context}}
- **When** {{action}}
- **Then** `file_finding.py`'s RFC template derives decision rows from the finding's real options instead of emitting the content-free boilerplate row
- **Verify:** {{executable check}}

### AC3: RFC0035/0037/0038/0039's D1 rows and RFC0042's D2 are closed with what actually shipped, with

- **Given** {{context}}
- **When** {{action}}
- **Then** RFC0035/0037/0038/0039's D1 rows and RFC0042's D2 are closed with what actually shipped, with revision rows
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
