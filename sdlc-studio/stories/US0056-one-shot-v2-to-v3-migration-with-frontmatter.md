# US0056: One-shot v2-to-v3 migration with frontmatter aliases and alias-aware readers

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0012
> **Persona:** Skill Maintainer
> **Source:** CR-0167 (WS2), RFC-0024
> **Depends on:** US0055

## User Story

**As a** consuming-project maintainer
**I want** a one-shot v2-to-v3 migration that maps old ids to ULIDs and keeps old ids as aliases
**So that** I upgrade once with historical order preserved and no broken inbound links

## Acceptance Criteria

### AC1: Order-preserving migration with aliases

- **Given** a v2 workspace of sequential-id artefacts
- **When** the migration runs
- **Then** each file gets a creation-date ULID, the old id is retained in `aliases:`, and
  listing order matches the pre-migration order
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate_v3.py -k order_and_alias

### AC2: Readers resolve old ids via alias; links stay green

- **Given** an artefact referenced by its old id elsewhere
- **When** any reader (reconcile, validate, transition, check_links) resolves it
- **Then** the alias resolves and `check_links.py` is clean after migration
- **Verify:** python3 tools/check_links.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
