# US0208: TRD: move critic record to writers and document the append-only atomic-write exception; harden read_verdicts against a torn row

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/critic.py
> **Epic:** EP0071
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: trd.md §3/§5 move `critic record` to the writer list (append-only verdict logs), keeping

- **Given** {{context}}
- **When** {{action}}
- **Then** trd.md §3/§5 move `critic record` to the writer list (append-only verdict logs), keeping critique/detect read-only
- **Verify:** {{executable check}}

### AC2: Rule 5 documents the append-only exception to the atomic-write guarantee (or the append is

- **Given** {{context}}
- **When** {{action}}
- **Then** Rule 5 documents the append-only exception to the atomic-write guarantee (or the append is hardened, e.g. single `O_APPEND` write per row)
- **Verify:** {{executable check}}

### AC3: `read_verdicts` surfaces a malformed/torn row as a warning instead of silently dropping it

- **Given** {{context}}
- **When** {{action}}
- **Then** `read_verdicts` surfaces a malformed/torn row as a warning instead of silently dropping it
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
