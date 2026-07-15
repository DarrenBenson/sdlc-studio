# US0156: Unified deterministic-vs-needs-human report, and apply the safe set only

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py
> **Epic:** EP0042
> **Points:** 5

## User Story

**As an** operator
**I want** migrate to apply only the deterministic set and report the rest
**So that** an upgrade never guesses a judgement (a breakdown, a triage, a re-size).

## Acceptance Criteria

### AC1: --apply writes only the deterministic set; needs-human items are never auto-applied

- **Given** a mixed project
- **When** `migrate --apply` runs
- **Then** it writes the deterministic set (a real version - never "unknown" - config, sizing conversions), leaves the needs-human items untouched (the accepted request still childless, the bug still without Points), and the render carries both sections
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_migrate.MigrateTests.test_apply_writes_only_the_deterministic_set tests.test_migrate.MigrateTests.test_render_has_both_sections
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
