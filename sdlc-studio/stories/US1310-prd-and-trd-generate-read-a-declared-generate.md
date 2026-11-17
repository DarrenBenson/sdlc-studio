# US1310: PRD and TRD generate read a declared `generate.runtime_inputs` folder of schema dumps, stored-procedure source and trace exports, cite each file used, and state that the skill never connects to a running system

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0737
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-prd.md, .claude/skills/sdlc-studio/reference-trd.md, .claude/skills/sdlc-studio/help/brownfield-runbook.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, tools/tests/test_generate_runtime_inputs.py
> **Epic:** EP0374
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** PRD and TRD generate read a declared `generate.runtime_inputs` folder of schema dumps, stored-procedure source and trace exports, cite each file used, and state that the skill never connects to a running system
**So that** CR0737 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A `generate.runtime_inputs` setting names a folder, and the PRD and TRD generate workflows instruct

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: A `generate.runtime_inputs` setting names a folder, and the PRD and TRD generate workflows instruct the agent to read it and to cite each file it drew a requirement from

### AC2: The workflows state that the skill reads exports only and never connects to a database or a running

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: The workflows state that the skill reads exports only and never connects to a database or a running service

### AC3: The brownfield runbook says what to export and where to put it

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
