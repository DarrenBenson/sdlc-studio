# US0192: verify_ac run --story resolves an id-shaped value as an id; a value that is neither path nor id fails naming both

> **Status:** Draft
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0062
> **Points:** 1

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** verify_ac run --story to accept a story id
**So that** the natural first invocation works instead of failing into --help

## Acceptance Criteria

### AC1: Id-shaped values resolve as ids

- **Given** run --story US0177 with no such file existing
- **When** verify_ac runs
- **Then** the story resolves by id; existing path behaviour unchanged
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_verify_ac.py -k StoryId

### AC2: Neither-path-nor-id fails naming both

- **Given** run --story with a value that is neither
- **When** verify_ac runs
- **Then** the error names the failed path lookup AND the failed id resolution
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_verify_ac.py -k StoryIdNeither

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
