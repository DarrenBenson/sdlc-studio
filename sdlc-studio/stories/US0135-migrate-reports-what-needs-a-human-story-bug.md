# US0135: migrate reports what needs a human: story/bug Effort has no clean Points mapping so flag for re-size, and childless-accepted requests flag for refine

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate_v3.py
> **Epic:** EP0037
> **Points:** 3

## User Story

**As an** operator upgrading an existing project
**I want** `migrate sizing` to report what it cannot convert safely, never guess
**So that** I re-size my delivery units in points and refine my accepted requests, rather than trust a bad auto-conversion.

## Acceptance Criteria

### AC1: a story/bug with Effort but no Points is flagged, not converted

- **Given** a story/bug carrying `Effort` but no `Points`
- **When** `migrate sizing` runs
- **Then** it is reported under `needs_resize` and NOT auto-converted (Effort has no honest Points map - RFC0038); a pointed delivery unit is not flagged
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate_sizing.py::SizingReportTests
- **Verified:** yes (2026-07-15)

### AC2: an accepted childless request is flagged for refine

- **Given** an accepted (Approved) childless request, and a still-Proposed intake one
- **When** `migrate sizing` runs
- **Then** the accepted childless request is reported under `needs_refine` (decompose with `refine apply`), reusing reconcile's one definition of an accepted-childless request; the intake one is not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate_sizing.py::SizingReportTests::test_accepted_childless_request_needs_refine
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
