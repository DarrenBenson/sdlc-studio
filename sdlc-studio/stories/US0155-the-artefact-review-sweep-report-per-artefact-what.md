# US0155: The artefact-review sweep: report per-artefact what needs refine, triage or resize

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py
> **Epic:** EP0042
> **Points:** 5

## User Story

**As an** operator
**I want** migrate to review every open artefact and name what each needs
**So that** nothing open is silently left behind, and I know the exact ceremony to run.

## Acceptance Criteria

### AC1: the sweep names each artefact's ceremony (refine/triage/resize) with the exact command

- **Given** an accepted childless request, a childless Issue, and a legacy-Effort delivery unit
- **When** `migrate` runs
- **Then** each appears under needs-human tagged needs-refine/needs-triage/needs-resize, each carrying the exact command (`refine apply --request`, `triage apply --issue`, a re-size instruction)
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_migrate.MigrateTests.test_the_artefact_sweep_names_each_ceremony_with_a_command
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
