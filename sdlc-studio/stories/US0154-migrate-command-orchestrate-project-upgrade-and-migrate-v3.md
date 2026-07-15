# US0154: migrate command: orchestrate project_upgrade and migrate_v3 sizing into one dry-run pass

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py
> **Epic:** EP0042
> **Points:** 5

## User Story

**As an** operator upgrading a project
**I want** one command that runs the existing upgrade pieces and aggregates them
**So that** I don't have to know to run project upgrade + migrate_v3 sizing separately.

## Acceptance Criteria

### AC1: migrate orchestrates the pieces into one dry-run report, no-op on a non-skill repo

- **Given** a project with conventions gaps and legacy-Effort containers
- **When** `migrate` runs (dry-run)
- **Then** it aggregates project_upgrade's conventions/version findings and migrate_v3's sizing conversions into one `deterministic` list, writes nothing, and returns not-applicable on a non-skill repo
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_migrate.MigrateTests.test_dry_run_aggregates_deterministic_and_needs_human_and_writes_nothing tests.test_migrate.MigrateTests.test_non_skill_repo_is_not_applicable
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
