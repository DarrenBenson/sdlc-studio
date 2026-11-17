# US1287: The three unreferenced persona prompt templates are retired or rewired, and a test fails on an unnamed persona template

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0726
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/personas/prompts/code-analysis-prompt.md, .claude/skills/sdlc-studio/templates/personas/prompts/discovery-presentation.md, .claude/skills/sdlc-studio/templates/personas/prompts/enrichment-questions.md, .claude/skills/sdlc-studio/reference-persona-generate.md, tools/tests/test_persona_templates_referenced.py
> **Epic:** EP0364
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The three unreferenced persona prompt templates are retired or rewired, and a test fails on an unnamed persona template
**So that** CR0726 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each of the three files is either removed from the shipped skill or named by

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: Each of the three files is either removed from the shipped skill or named by reference-persona-generate.md as the prompt it loads for a stated step

### AC2: Any file that is kept asks for a Cast role and End Goals and no longer classifies a persona as Team

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: Any file that is kept asks for a Cast role and End Goals and no longer classifies a persona as Team to be assigned to an amigo, in agreement with persona-template.md

### AC3: A test in tools/tests/`test_persona_templates_referenced.py` fails when a file under

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: A test in tools/tests/`test_persona_templates_referenced.py` fails when a file under templates/personas/ is named by no shipped reference page, help page or script

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
