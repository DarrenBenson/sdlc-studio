# US1176: The release gate lists a declared non-completing status's failing criteria as unbuilt, and an undeclared one still fails

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0636
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_gate_declared_status.py
> **Epic:** EP0317
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The release gate lists a declared non-completing status's failing criteria as unbuilt, and an undeclared one still fails
**So that** CR0636 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A project can declare an extended status as not claiming completion in .config.yaml; the release

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: A project can declare an extended status as not claiming completion in .config.yaml; the release gate then lists that story's failing criteria as unbuilt, and an undeclared extended status still fails. The stories refine writes carry the executable checks.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
