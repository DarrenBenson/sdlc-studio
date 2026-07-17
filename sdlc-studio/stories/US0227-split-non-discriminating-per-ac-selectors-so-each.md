# US0227: split non-discriminating per-AC selectors so each AC fails on its own regression

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories/US0172-per-attempt-telemetry-records-carry-an-attempts-list.md, sdlc-studio/stories/US0173-true-cost-with-rework-unit-cost-sums-priced.md
> **Epic:** EP0075
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

> Seeded from the request's full criteria list - redistribute across this epic's stories as you groom them.

### AC1: US0172 and US0173 select distinct test classes/methods so each AC fails on a regression in its own

- **Given** {{context}}
- **When** {{action}}
- **Then** US0172 and US0173 select distinct test classes/methods so each AC fails on a regression in its own behaviour
- **Verify:** {{executable check}}

### AC2: US0163 and US0166 per-AC Verify lines are narrowed (-k per AC) rather than whole-file

- **Given** {{context}}
- **When** {{action}}
- **Then** US0163 and US0166 per-AC Verify lines are narrowed (-k per AC) rather than whole-file
- **Verify:** {{executable check}}

### AC3: Optional: a verify lint flags byte-identical Verify commands appearing under different ACs/stories

- **Given** {{context}}
- **When** {{action}}
- **Then** Optional: a verify lint flags byte-identical Verify commands appearing under different ACs/stories
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
