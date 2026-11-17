# US1227: The amigo template and the project's seat cards carry the hand-back section, and validate seats warns if not

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0686
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/personas/amigo-template.md, sdlc-studio/personas/seats/qa.md, sdlc-studio/personas/seats/engineering.md, sdlc-studio/personas/seats/product.md, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0335
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The amigo template and the project's seat cards carry the hand-back section, and validate seats warns if not
**So that** CR0686 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: `templates/personas/amigo-template.md` carries the hand-back section, worded as in the shipped

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: `templates/personas/amigo-template.md` carries the hand-back section, worded as in the shipped amigo seats

### AC2: `validate seats` warns when a project seat card that overrides a shipped seat has no hand-back

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: `validate seats` warns when a project seat card that overrides a shipped seat has no hand-back section, naming the card

### AC3: This repository's seat cards under `sdlc-studio/personas/seats/` carry the section, and a test

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: This repository's seat cards under `sdlc-studio/personas/seats/` carry the section, and a test fails when the template or a shipped seat loses it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
