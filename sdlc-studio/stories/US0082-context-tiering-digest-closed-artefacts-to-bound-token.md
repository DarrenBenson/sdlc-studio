# US0082: Context tiering: digest closed artefacts to bound token cost

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0018
> **Persona:** Skill Maintainer
> **Source:** CR-0179

## User Story

**As a** maintainer of a long-lived repo
**I want** closed artefacts archived into summarised digests that status/planning reads
**So that** token cost stops creeping as the corpus ages, without losing the audit trail

## Acceptance Criteria

### AC1: Digests read instead of originals, drift-checked

- **Given** a fixture repo with 500+ closed artefacts
- **When** status/hint runs
- **Then** it reads mechanical digests (not originals), token cost drops measurably, and a stale
  digest is drift that reconcile regenerates
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_context_tiering.py

### AC2: Originals still resolve, small repos unchanged

- **Given** a specific closed artefact id (alias included) and a repo below the threshold
- **When** opened / operated
- **Then** the full original resolves and sub-threshold repos see no behaviour change
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_context_tiering.py -k threshold

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
