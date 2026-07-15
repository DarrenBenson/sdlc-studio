# US0157: Document migrate in reference-upgrade, help and the CHANGELOG

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-upgrade.md
> **Epic:** EP0042
> **Points:** 3

## User Story

**As an** operator
**I want** migrate documented where the other upgrade commands are
**So that** I can reach for it as the "bring this up to date" front door.

## Acceptance Criteria

### AC1: migrate is documented (reference-upgrade, help, script catalogue, CHANGELOG) and coverage + links pass

- **Given** the migrate documentation
- **When** the docs are checked
- **Then** `reference-upgrade.md` carries a migrate section + row, `migrate.py` has a reference-scripts entry, `migrate` is in the SKILL Type Reference and help catalogue, the CHANGELOG covers it, and doc-coverage + links pass
- **Verify:** shell grep -q '## migrate' .claude/skills/sdlc-studio/reference-upgrade.md && python3 .claude/skills/sdlc-studio/scripts/doc_coverage.py && python3 tools/check_links.py
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
