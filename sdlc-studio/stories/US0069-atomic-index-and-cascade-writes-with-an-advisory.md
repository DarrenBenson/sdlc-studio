# US0069: Atomic index and cascade writes with an advisory allocation lock

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0015
> **Persona:** Skill Maintainer
> **Source:** CR-0183

## User Story

**As a** skill maintainer running agent waves
**I want** atomic index/cascade writes and an advisory allocation lock
**So that** the ledger is passively safe under concurrent writes when orchestration fails

## Acceptance Criteria

### AC1: No lost writes, no torn files

- **Given** two concurrent `artifact.py new` calls (different titles)
- **When** they allocate and write
- **Then** they never mint the same id, and a crash mid-index-write leaves the prior `_index.md`
  intact (write-temp-then-rename)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_concurrency.py

### AC2: Uncontended path unaffected; lock self-heals

- **Given** the single-writer common case
- **When** it runs
- **Then** there is no measurable regression and a stale lock is reclaimed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_concurrency.py -k stale_lock

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
