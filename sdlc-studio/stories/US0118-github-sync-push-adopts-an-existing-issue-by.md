# US0118: github_sync push adopts an existing issue by title instead of blind create

> **Status:** Done
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new
> **Epic:** EP0027
> **Persona:** sync operator (dogfooding)
> **CR:** CR0206

## User Story

**As a** person running `github_sync push`
**I want** a re-run after a crashed or timed-out create to adopt the issue that was made, not make a second one
**So that** a transient failure never leaves duplicate GitHub issues for one record

## Context

RV0007: `cmd_push` created an issue then stamped the local file. A crash between them - or a
`gh` timeout after the server accepted the request - left the record unstamped, and the re-run
created a second issue for the same record. Nothing checked for an existing `[rec_id]`-titled
issue first.

## Acceptance Criteria

### AC1: an existing [rec_id]-titled issue is adopted, not duplicated

- **Given** an unmapped local CR whose `[CR-0001]`-titled issue already exists on GitHub
- **When** `push` runs
- **Then** the record is stamped with the existing issue number and no new issue is created
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py -k adopts_titled_issue
- **Verified:** yes (2026-07-10)

### AC2: a genuinely new record still creates

- **Given** an unmapped record with no matching remote issue
- **When** `push` runs
- **Then** a new issue is created and the record stamped with it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py -k creates_issue_for_unmapped
- **Verified:** yes (2026-07-10)

### AC3: a hash-matched mapped record is still skipped (idempotent)

- **Given** a mapped record whose body hash matches its recorded state
- **When** `push` runs
- **Then** that record's issue is not edited
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py -k idempotent_when_hash
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
| 2026-07-10 | sprint (CR0206 decomposition) | ACs authored from the RV0007 finding |
