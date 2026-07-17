# US0222: persist verification-cap overflow as a durable carry-over worklist a scoped follow-up re-ingests

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/templates/automation/audit-finder.md
> **Epic:** EP0073
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: reference-audit.md budget section requires writing capped-out candidates (full JSON: title, file

- **Given** {{context}}
- **When** {{action}}
- **Then** reference-audit.md budget section requires writing capped-out candidates (full JSON: title, file, claim, evidence, lens, severity) to a durable carry-over file (e.g. .local/audit-carryover-<date>.json), not just logging the count
- **Verify:** {{executable check}}

### AC2: The audit close-out report names the carry-over file and the one-line scoped command that verifies

- **Given** {{context}}
- **When** {{action}}
- **Then** The audit close-out report names the carry-over file and the one-line scoped command that verifies just those candidates (skipping find)
- **Verify:** {{executable check}}

### AC3: A follow-up run can ingest the carry-over file as its candidate pool directly, running refute

- **Given** {{context}}
- **When** {{action}}
- **Then** A follow-up run can ingest the carry-over file as its candidate pool directly, running refute panels without re-finding
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
