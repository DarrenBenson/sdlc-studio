# US0068: Optional tranche reference field, record-only

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0014
> **Persona:** Orchestrator / Operator
> **Source:** CR-0172
> **Depends on:** -

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
- **Verified:** yes (2026-07-08)

### AC2: Ledger answers the delivery question

- **Given** artefacts carrying a tranche reference
- **When** status/reconcile is queried
- **Then** it lists everything in a given tranche from the ledger alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py -k tranche_query
- **Verified:** yes (2026-07-08)

## Design Notes (groomed 2026-07-08, see D0015)

- **Record-only:** `validate.py` accepts a present or absent `tranche:` value, fails only an
  empty/non-string value; no sdlc-studio code path writes it except orchestrator pass-through
  (sdlc-studio is a system of record, not a scheduler).
- **Ledger query:** `status.py`/`reconcile` can list everything carrying a given tranche
  reference from the ledger alone.
- **Era-gated** under `schema_version: 3`. Fully independent of US0065-0067.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | sdlc | Groomed to Ready: scope confirmed record-only (D0015) |
