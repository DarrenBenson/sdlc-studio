# US0252: sweep the remaining bare artefact-body read_text calls through read_text_safe, with a regression test

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/deploy.py, .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Epic:** EP0082
> **Points:** 2

## User Story

**As an** agent scanning a workspace
**I want** every artefact-body read to survive a non-UTF-8 file
**So that** one corrupt artefact from a crashed session cannot abort a whole pass

## Acceptance Criteria

### AC1: Artefact-body reads route through read_text_safe

- **Given** shipped scripts still read an artefact body with a bare `read_text(encoding="utf-8")`
- **When** the scripts tree is swept for artefact-body read sites
- **Then** every one goes through `sdlc_md.read_text_safe`, and the sweep fails when a new bare read arrives
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_repo_hygiene.py -k BareArtefactReadSweepTests
- **Verified:** yes (2026-07-19)

### AC2: A non-UTF-8 artefact does not crash a scanner

- **Given** a fixture workspace holding an artefact whose body is not valid UTF-8
- **When** each swept scanner runs over that workspace
- **Then** it completes and names the file rather than raising UnicodeDecodeError
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_reconcile.py -k NonUtf8ScannerRegressionTests
- **Verified:** yes (2026-07-19)

### AC3: Index-file reads stay loud

- **Given** an `_index.md` that is unreadable or not valid UTF-8
- **When** a scanner reads it
- **Then** the failure surfaces rather than being silently defaulted to an empty body, so derived-index drift is never masked
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_reconcile.py -k LoudIndexReadTests
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
