# US0355: decide and document the Primary-selection method in reference-persona.md and fill the D1 row

> **Status:** Ready
> **Delivers:** CR0346
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0122
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-persona.md, sdlc-studio/decisions.md

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the Primary-selection method is documented

- **Given** reference-persona.md, which today contains no Primary-selection rule at all
- **When** a reader asks how the Primary is chosen when several candidates compete
- **Then** the document carries a `## Choosing the Primary` section stating the method and its tie-break, distinguished from the one-Primary-per-interface constraint. Greping for `Primary` would be vacuous - that constraint already uses the word; the check must bind the section that does not yet exist
- **Verify:** grep '## Choosing the Primary' .claude/skills/sdlc-studio/reference-persona.md
- **Verified:** no (2026-07-24)

### AC2: RFC0017's D1 row is closed with what was decided

- **Given** RFC0017's D1 row, Open since the RFC was accepted
- **When** `validate` reads the RFC
- **Then** the row is closed and the accepted-open-decision error does not fire - the row sat unnoticed because a 5-column table was unparseable by the first accept gate, so closing it must be verified by the gate, not by eye
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/validate.py check --root . 2>&1 | grep -q 'RFC0017.*accepted-open-decision' && exit 1 || exit 0

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
