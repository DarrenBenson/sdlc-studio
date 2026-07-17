# US0208: TRD: move critic record to writers and document the append-only atomic-write exception; harden read_verdicts against a torn row

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/critic.py
> **Epic:** EP0071
> **Points:** 3

## User Story

**As an** engineer reading the write contract
**I want** `critic record` classed as a writer, the append-only exception documented, and torn rows surfaced
**So that** the spec matches the shipped critic and a truncated verdict row is never silently lost

## Acceptance Criteria

### AC1: trd.md §3/§5 move `critic record` to the writer list (append-only verdict logs), keeping

- **Given** §3 and §5 listed `critic` among the read-only helpers, though `record`/`evidence`/`signoff` append to committed logs
- **When** the read-only entry becomes `critic brief`/`show` and `critic record` joins the authoring writers
- **Then** trd.md §3/§5 move `critic record` to the writer list (append-only verdict logs), keeping critique/detect read-only
- **Verify:** grep "critic record. appends to the committed verdict" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

### AC2: Rule 5 documents the append-only exception to the atomic-write guarantee (or the append is

- **Given** rule 5 claimed all shared-file writes go through `atomic_write`, but the verdict/telemetry/verify-history logs are append-only
- **When** rule 5 names the append-only ledgers as the deliberate exception (a single `O_APPEND` row write)
- **Then** Rule 5 documents the append-only exception to the atomic-write guarantee (or the append is hardened, e.g. single `O_APPEND` write per row)
- **Verify:** grep "append-only ledgers" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

### AC3: `read_verdicts` surfaces a malformed/torn row as a warning instead of silently dropping it

- **Given** `read_verdicts` kept 6-col and 5-col rows and silently dropped any other cell count, so a torn row vanished
- **When** the parser emits a stderr warning naming the malformed row before skipping it (RED-first test added)
- **Then** `read_verdicts` surfaces a malformed/torn row as a warning instead of silently dropping it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RecordTests::test_torn_row_surfaces_a_warning_not_silent_drop
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
