# US1303: `handoff show` prints each remaining item's Points and seat, and totals remaining points by suitability tag and by seat

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0733
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/help/sprint.md, tools/tests/test_handoff_effort.py
> **Epic:** EP0370
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** `handoff show` prints each remaining item's Points and seat, and totals remaining points by suitability tag and by seat
**So that** CR0733 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each remaining item in `handoff show` carries its Points, or the word unsized when it has none, in

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: Each remaining item in `handoff show` carries its Points, or the word unsized when it has none, in both the text and the JSON output

### AC2: Each remaining item names one seat, derived from the stage it stalled at by a rule the help page

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: Each remaining item names one seat, derived from the stage it stalled at by a rule the help page states

### AC3: The handoff ends with remaining points totalled by suitability tag and by seat, and the totals

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: The handoff ends with remaining points totalled by suitability tag and by seat, and the totals re-add from the rows

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
