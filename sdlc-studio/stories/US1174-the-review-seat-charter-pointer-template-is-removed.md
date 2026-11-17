# US1174: The review seat charter pointer template is removed and the persona template reference test covers pointer files

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0727
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/personas/review-seat-charter.md, tools/tests/test_persona_templates_referenced.py
> **Epic:** EP0315
> **Points:** 1
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The review seat charter pointer template is removed and the persona template reference test covers pointer files
**So that** CR0727 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: templates/personas/review-seat-charter.md is no longer in the shipped skill

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

### AC2: A search of the shipped skill, install.sh, install.ps1 and tools/ finds no path reference to

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: A search of the shipped skill, install.sh, install.ps1 and tools/ finds no path reference to review-seat-charter.md that expects the file to exist

### AC3: A test in tools/tests/`test_persona_templates_referenced.py` fails when a file under

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: A test in tools/tests/`test_persona_templates_referenced.py` fails when a file under templates/personas/ is named by no shipped reference page, help page or script, so a pointer kept for references that no longer exist is caught

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
