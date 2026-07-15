# US0136: the upgrade guide reference doc plus a CHANGELOG breaking-change section for the 5.0.0 cut

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-upgrade.md
> **Epic:** EP0037
> **Points:** 2

## User Story

**As an** operator upgrading an existing project
**I want** a written upgrade guide and a CHANGELOG breaking-change note
**So that** I can follow the three-step path (migrate, refine, enforce) without reverse-engineering it from the code.

## Acceptance Criteria

### AC1: the upgrade guide documents the three-step path and links resolve

- **Given** the two-backlog migration
- **When** `reference-upgrade.md#two-backlog-migration` is read
- **Then** it documents the three steps (`migrate_v3.py sizing`, `refine`, `two_backlog.enforce`), the deterministic-vs-flagged split, and rollback; the CHANGELOG carries a breaking-change note; and all markdown links resolve
- **Verify:** shell python3 tools/check_links.py
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
