# US0055: ULID id generator across artifact.py, next_id.py and file_finding.py

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0012
> **Persona:** Skill Maintainer
> **Source:** CR-0167 (WS1), RFC-0024

## User Story

**As a** skill maintainer
**I want** every allocator to mint a type-prefixed short ULID instead of a sequential number
**So that** two agents in separate worktrees never collide on an id, with no coordination

## Acceptance Criteria

### AC1: Collision-free concurrent allocation

- **Given** two `artifact.py new` calls run in separate worktrees on the same trunk
- **When** both allocate an id of the same type
- **Then** the ids are distinct and both merge cleanly
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py -k ulid_concurrent

### AC2: Creation-order sort preserved

- **Given** a directory of ULID-named artefacts created in sequence
- **When** the directory is listed lexicographically
- **Then** the order equals creation order (the timestamp prefix)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py -k ulid_sorts

### AC3: All allocators switched

- **Given** `artifact.py`, `next_id.py` and `file_finding.py`
- **When** any allocates an id
- **Then** it emits the `{TYPE}-{ULID}` format (8-char suffix, extended on a directory clash)
- **Verify:** grep .claude/skills/sdlc-studio/scripts/next_id.py "ulid"

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
