# US0356: remove the Decision-Override from RFC0017 once D1 closes

> **Status:** Draft
> **Delivers:** CR0346
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0122
> **Points:** 1
> **Affects:** sdlc-studio/rfcs/RFC0017-agent-persona-selection.md, sdlc-studio/decisions.md

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the Decision-Override is removed once D1 is closed

- **Given** RFC0017 carrying a Decision-Override placed there while D1 was open
- **When** D1 is closed
- **Then** the override is removed and the RFC's decision section stands on the recorded ruling alone - an override outliving the gap it covered is a standing exemption nobody chose
- **Verify:** shell grep -q 'Decision-Override' sdlc-studio/rfcs/RFC0017*.md && exit 1 || exit 0

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
