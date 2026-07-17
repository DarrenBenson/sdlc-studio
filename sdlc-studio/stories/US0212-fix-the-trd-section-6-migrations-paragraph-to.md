# US0212: Fix the TRD section 6 Migrations paragraph to name the shipped migration scripts

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md
> **Epic:** EP0071
> **Points:** 2

## User Story

**As an** engineer reading §6 Migrations
**I want** the shipped migration script surface named and reconciled with SKILL.md's type table
**So that** the paragraph stops claiming migration is doc-only when migrate.py/project_upgrade.py/migrate_v3.py exist

## Acceptance Criteria

### AC1: §6 Migrations names the shipped script surface (migrate.py orchestrator, `project_upgrade.py`

- **Given** §6 Migrations said schema migration is "handled by reference-upgrade.md ... not by the script layer", contradicting the shipped scripts
- **When** the paragraph names migrate.py (orchestrator), project_upgrade.py (`--apply` safe set) and migrate_v3.py, alongside reference-upgrade.md
- **Then** §6 Migrations names the shipped script surface (migrate.py orchestrator, `project_upgrade.py` --apply safe set, `migrate_v3.py)` alongside reference-upgrade.md
- **Verify:** grep "project_upgrade.py. migrates a consuming project" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

### AC2: The upgrade-vs-migrate type naming is reconciled with SKILL.md's type table

- **Given** the paragraph blurred `upgrade` (the operator-facing type in SKILL.md's table) with `migrate` (the orchestrator command)
- **When** it states the operator-facing surface is the `upgrade` type per SKILL.md's table, with migrate.py/project_upgrade.py/migrate_v3.py as the scripts under it
- **Then** The upgrade-vs-migrate type naming is reconciled with SKILL.md's type table
- **Verify:** grep "operator-facing surface is the .upgrade. type" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
