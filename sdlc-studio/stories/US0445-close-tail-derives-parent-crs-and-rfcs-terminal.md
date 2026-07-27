# US0445: Close tail derives parent CRs and RFCs terminal when all their children are terminal

> **Status:** Draft
> **Delivers:** CR0422
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0164
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: after `apply-signoff` marks an epic terminal, a CR/RFC all of whose decomposed epics (and any

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: after `apply-signoff` marks an epic terminal, a CR/RFC all of whose decomposed epics (and any directly-linked delivered stories) are terminal is itself transitioned to its terminal status (Complete for a CR, the RFC's terminal for an RFC)

### AC2: a CR/RFC with at least one non-terminal child is left unchanged - the derivation is

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: a CR/RFC with at least one non-terminal child is left unchanged - the derivation is all-children-terminal, the same rule the epic derivation already uses

### AC3: the close output names each CR/RFC it derived terminal, as it already names the epics, so the

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: the close output names each CR/RFC it derived terminal, as it already names the epics, so the cascade is visible and auditable

### AC4: the derivation is idempotent and safe on a mixed batch (bug-only or story-only batches with no

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: the derivation is idempotent and safe on a mixed batch (bug-only or story-only batches with no parent CR derive nothing, no error)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
