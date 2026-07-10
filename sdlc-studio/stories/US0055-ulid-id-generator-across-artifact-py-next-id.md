# US0055: ULID id generator across artifact.py, next_id.py and file_finding.py

> **Status:** Done
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
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_concurrency.py .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py -k "concurrent_new_mints_distinct_ids or short_id_carries_randomness"
- **Verified:** yes (2026-07-10)

### AC2: Creation-order sort preserved

- **Given** a directory of ULID-named artefacts created in sequence
- **When** the directory is listed lexicographically
- **Then** the order equals creation order (the timestamp prefix)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py -k "short_id_sorts_by_time or new_ulid_is_sortable"
- **Verified:** yes (2026-07-10)

### AC3: All allocators switched

- **Given** the id-creating allocators - `artifact.py` and `file_finding.py`, both
  minting through the shared `sdlc_md` ULID path (`next_id.py` has since become the
  sequential-era allocator only; wording aligned 2026-07-10)
- **When** any allocates an id on a schema-v3 project
- **Then** it emits the `{TYPE}-{ULID}` format (8-char suffix, extended on a directory clash)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k "mints_ulid or mints_a_ulid"
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
