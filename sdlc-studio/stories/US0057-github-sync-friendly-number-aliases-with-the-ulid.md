# US0057: GitHub-sync friendly-number aliases with the ULID staying canonical

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0012
> **Persona:** Skill Maintainer
> **Source:** CR-0167 (WS3), RFC-0024

## User Story

**As a** GitHub-syncing operator
**I want** friendly issue numbers recorded as aliases while the ULID stays canonical
**So that** humans get readable numbers without the tool losing its local-first, offline identity

## Acceptance Criteria

### AC1: Friendly number is an alias, never the identity

- **Given** an artefact synced to a GitHub issue
- **When** sync allocates the issue number
- **Then** the number is stored as an alias and the ULID remains the canonical id in the filename
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py -k friendly_alias

### AC2: Offline sync round-trip degrades cleanly

- **Given** no network / sync skipped
- **When** the tool operates
- **Then** identity is unaffected and nothing degrades
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py -k offline

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
