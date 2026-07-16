# US0187: refine copies the request's acceptance criteria into minted stories as AC scaffolds with Verify placeholders, --no-seed-acs opt-out

> **Status:** Draft
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Epic:** EP0057
> **Points:** 3

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** refine to seed each minted story's ACs from the request's own acceptance criteria
**So that** the exact checkable criteria the request already states stop being re-typed by hand into placeholder scaffolds

## Acceptance Criteria

### AC1: Request ACs become story AC scaffolds

- **Given** a request with '- [ ]' acceptance criteria
- **When** refine apply mints its stories
- **Then** each criterion becomes an AC block (title from the text, Given/When/Then to author, Verify left as an explicit placeholder)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_refine.py -k SeedAcs

### AC2: Seeding never fakes readiness

- **Given** a story with seeded Verify placeholders
- **When** validate/critic inspect it
- **Then** the placeholder is still flagged until made executable - seeding transcribes, it does not green
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_refine.py -k SeedNotReady

### AC3: Opt-out preserved

- **Given** refine apply --no-seed-acs
- **When** stories are minted
- **Then** the bare scaffold behaviour is byte-identical to today
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_refine.py -k SeedOptOut

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
