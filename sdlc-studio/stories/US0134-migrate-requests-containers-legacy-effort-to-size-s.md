# US0134: migrate requests/containers: legacy Effort to Size (S/M/L direct), a pointed cr/rfc/epic gets Size from the point band, idempotent with dry-run

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate_v3.py
> **Epic:** EP0037
> **Points:** 3

## User Story

**As an** operator upgrading an existing project
**I want** `migrate sizing` to convert my requests and containers to the new T-shirt Size deterministically
**So that** my old CRs/RFCs/epics carry the sizing field the new model reads, without me editing each by hand.

## Acceptance Criteria

### AC1: a cr/rfc/epic's legacy Effort or Points becomes a Size

- **Given** a cr/rfc/epic carrying a legacy `Effort:` (S/M/L) or `Points:` and no `Size:`
- **When** `migrate_v3.migrate_sizing(root, dry_run=False)` runs
- **Then** it writes a `Size:` - the matching S/M/L for an Effort, or the point-band size for a pointed one; an already-sized artefact is skipped (idempotent), and a dry-run reports without writing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate_sizing.py::SizingConversionTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
