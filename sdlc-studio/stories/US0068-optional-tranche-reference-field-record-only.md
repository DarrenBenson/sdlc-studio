# US0068: Optional tranche reference field, record-only

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0014
> **Persona:** Orchestrator / Operator
> **Source:** CR-0172

## User Story

**As an** external orchestrator
**I want** to record a tranche reference on an artefact that sdlc-studio only reads, never allocates
**So that** the ledger can answer "what shipped in tranche 12" while staying a system of record, not a scheduler

## Acceptance Criteria

### AC1: Optional record-only field

- **Given** a CR/bug/story/epic
- **When** a `tranche:` value is present or absent
- **Then** validate passes both, fails only an empty/non-string value, and no code path writes it
  except orchestrator pass-through
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k tranche_shape

### AC2: Ledger answers the delivery question

- **Given** artefacts carrying a tranche reference
- **When** status/reconcile is queried
- **Then** it lists everything in a given tranche from the ledger alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py -k tranche_query

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
