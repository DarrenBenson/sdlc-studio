# US0106: v3 to v4 upgrade walk rehearsed on two consuming projects with findings filed

> **Status:** Done
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0024
> **Persona:** Engineering seat
> **Affects:** scripts/project_upgrade.py, scripts/migrate_v3.py, scripts/tests/test_project_upgrade.py, sdlc-studio/reviews
> **Depends on:** US0105

## User Story

**As a** maintainer proving v4 is safe before rc1
**I want** `project upgrade` on a v2 project to present the v2 to v3 migration as a directed sequence, rehearsed end to end on two real consuming projects
**So that** the "tested in anger" gate is evidence in files, not a claim, and any migration defect is caught before the default flip reaches users

Delivers CR0198 item 2 (the upgrade walk and its rehearsal gate).

## Acceptance Criteria

### AC1: project upgrade presents the migration as a directed sequence

- **Given** a v2 fixture project
- **When** `project upgrade` runs
- **Then** it presents the ordered walk (capability delta -> `migrate_v3` dry-run -> apply -> re-baseline) rather than a single opaque step
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::UpgradeWalkTests
- **Verified:** yes (2026-07-09)

### AC2: the walk is rehearsed dry-run on two real consuming projects, findings filed

- **Given** two real consuming projects
- **When** the walk is rehearsed dry-run against each
- **Then** a rehearsal-evidence record exists (project names redacted for neutrality), listing the outcome and linking any finding filed as a Bug/CR
- **Verify:** file sdlc-studio/reviews/v4-migration-rehearsal.md
- **Verified:** yes (2026-07-09)

### AC3: the rehearsal evidence is neutral (no private project name leaks)

- **Given** the rehearsal-evidence record
- **When** the neutrality guard runs
- **Then** it carries no blocklisted consuming-project name
- **Verify:** shell python3 tools/check_neutrality.py
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0198 item 2 (upgrade walk + rehearsal gate) |
