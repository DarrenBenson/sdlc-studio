# US0249: decide and act on the 5 help-only commands (lessons/repo/retro/review/upgrade): promote spine-serving ones, retire/redirect the rest

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/help/help.md
> **Epic:** EP0081
> **Points:** 3

## User Story

**As an** operator reading the command surface
**I want** each of the five help-only commands either promoted into the SKILL Type
Reference or retired out of the catalogue
**So that** the two surfaces agree and no command exists in one place only

## Acceptance Criteria

### AC1: Promote the spine-serving help-only commands

- **Given** `lessons`, `repo`, `retro`, `review` and `upgrade` appear in
  `help/help.md` but not in the SKILL.md Type Reference (the audit's five drift rows)
- **When** each is dispositioned against the process spine and the keepers are promoted
- **Then** every promoted command has a Type Reference row with a one-line
  description, and the audit reports it present in both surfaces
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_command_audit.HelpOnlyPromotionTests
- **Verified:** yes (2026-07-19)

### AC2: Retire the rest out of both surfaces, leaving a redirect

- **Given** a help-only command dispositioned retire rather than promote
- **When** the cleanup is applied to `help/help.md` and SKILL.md
- **Then** the command appears in neither surface, and `help/help.md` carries one
  redirect line naming what replaces it, so an operator following an old habit is not
  left with a dead route
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_command_audit.RetiredCommandAbsenceTests
- **Verified:** yes (2026-07-19)

### AC3: No command is left half-in

- **Given** the promote and retire edits touch SKILL.md and `help/help.md` together
- **When** `doc_coverage` and `command_audit` run over the working tree
- **Then** doc coverage passes and the audit counts zero drift: no command sits in the
  Type Reference without a help entry, or in help without a Type Reference row
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/doc_coverage.py && python3 .claude/skills/sdlc-studio/scripts/command_audit.py --format json | python3 -c "import json,sys; assert json.load(sys.stdin).get('summary', {}).get('drift') == 0"
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
