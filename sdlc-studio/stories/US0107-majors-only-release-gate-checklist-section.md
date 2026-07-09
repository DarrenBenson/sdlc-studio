# US0107: Majors-only release-gate checklist section

> **Status:** Done
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0024
> **Persona:** Engineering seat
> **Affects:** templates/workflows/release-gate.md, tools/check_links.py

## User Story

**As a** maintainer cutting a major release
**I want** the release-gate checklist to carry a majors-only section
**So that** a breaking release re-runs the extra steps (breaking-change inventory, migration-rehearsal evidence, eval re-run, doc sweep, rc tag + soak) that a patch release skips

Delivers CR0198 item 3.

## Acceptance Criteria

### AC1: release-gate.md gains a majors-only section

- **Given** `templates/workflows/release-gate.md`
- **When** it is read
- **Then** it has a "Majors only" section listing: breaking-change inventory named in the CHANGELOG, migration-rehearsal evidence linked, eval scenarios re-run, README/docs saying the new major, and an rc tag cut from a green gate with a soak window before the final tag
- **Verify:** grep "Majors only" .claude/skills/sdlc-studio/templates/workflows/release-gate.md
- **Verified:** yes (2026-07-09)

### AC2: the new section's anchor links resolve

- **Given** the edited checklist
- **When** the link guard runs
- **Then** every markdown anchor still resolves
- **Verify:** shell python3 tools/check_links.py
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0198 item 3 (majors-only checklist) |
