# US0141: Document the discovery track: Issue and triage help, reference and README

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/triage.md
> **Epic:** EP0038
> **Points:** 3

## User Story

**As an** operator new to the discovery track
**I want** help, reference, README and CHANGELOG coverage of Issue and triage
**So that** I can use them without reverse-engineering from the code.

## Acceptance Criteria

### AC1: the help/reference/README/CHANGELOG exist and all markdown links resolve

- **Given** the discovery-track documentation
- **When** the docs are checked
- **Then** `help/issue.md` and `help/triage.md` exist, `reference-scripts-create.md` documents `triage.py`, the CHANGELOG carries the Added entries, and every markdown link resolves
- **Verify:** shell test -f .claude/skills/sdlc-studio/help/issue.md && test -f .claude/skills/sdlc-studio/help/triage.md && python3 tools/check_links.py
- **Verified:** yes (2026-07-15)

### AC2: the docs pass style and budget guards

- **Given** the new and edited markdown
- **When** the style and budget guards run
- **Then** no em-dash, jargon, American spelling or provenance-tag violation, and no file over its line budget
- **Verify:** shell bash tools/lint-style.sh && python3 tools/check_budgets.py
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
