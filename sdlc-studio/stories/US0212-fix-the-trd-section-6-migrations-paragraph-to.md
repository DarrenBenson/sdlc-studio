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

### AC2: The upgrade-vs-migrate type naming is reconciled with SKILL.md's type table (restated by CR0365)

- **Given** the paragraph blurred `upgrade` with `migrate` (the orchestrator command)
- **When** it names the operator-facing types SKILL.md's table actually carries
- **Then** the naming is reconciled with the table as it stands. The original wording pinned
  an `upgrade` row in that table; CR0365 measured it and found no such row, so the claim this
  AC asserted was false and its verifier could never pass. The paragraph now states that the
  table lists `migrate` and `skill-update` and carries no `upgrade` row, with
  `reference-upgrade.md` reached from the Progressive Loading Guide
- **Verify:** grep "type table lists both and carries no" sdlc-studio/trd.md
- **Verified:** yes (2026-07-27)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | BG0303 | AC2's grep pinned a sentence CR0365 removed because the claim in it was false, leaving a Done story whose verifier could never pass. The AC is restated to what shipped and re-pointed at the present wording; the falsified `upgrade`-row claim is recorded here rather than quietly dropped |
