# US0038: provenance stamp misuse check and remake

> **Status:** Done
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Epic:** EP0008

## User Story

**As a** team adopting SDLC Studio
**I want** tool-created artifacts stamped and hand-authored ones flagged, with a backfill
**So that** deterministic creation becomes the checkable, enforceable path (CR0052).

## Acceptance Criteria

### AC1: stamp + check (advisory, adoption-cutoff, opt-in enforce)

- **Given** stamped and un-stamped artifacts
- **When** `provenance check` runs
- **Then** it flags only un-stamped artifacts past `provenance.adopt_after` (legacy exempt), advisory by default, blocking only when `provenance.enforce`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_provenance.py::CheckTests
- **Verified:** yes (2026-06-21)

### AC2: remake backfills the stamp - content-preserving, idempotent, dry-run

- **Given** un-stamped artifacts
- **When** `remake` runs (dry-run then real)
- **Then** dry-run reports without writing, the real run adds the stamp preserving all content, and a second run changes nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_provenance.py::RemakeTests
- **Verified:** yes (2026-06-21)

### AC3: stamp detection + insertion are content-safe

- **Given** an artifact body
- **When** the stamp is detected/added
- **Then** `has_stamp` is exact and `_add_stamp` inserts one line idempotently without losing content
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_provenance.py::StampTests
- **Verified:** yes (2026-06-21)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0052) | Created via `new` (deterministic) |
