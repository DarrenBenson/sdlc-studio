# US0188: changelog fragments: per-unit files in changelog.d, deterministic compose into [Unreleased], release gate refuses stray fragments

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py, .claude/skills/sdlc-studio/reference-outputs.md
> **Epic:** EP0058
> **Points:** 5

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** each unit's changelog entry to live in its own fragment file, composed deterministically
**So that** per-unit commits stop contending on CHANGELOG.md and the hold-back dance dies

## Acceptance Criteria

### AC1: Fragments compose idempotently

- **Given** fragment files under changelog.d/ with section markers
- **When** changelog.py compose runs
- **Then** entries fold into CHANGELOG.md's [Unreleased] under Added/Changed/Fixed, idempotently (a second run changes nothing)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_changelog.py -k Compose
- **Verified:** yes (2026-07-16)

### AC2: A release refuses stray fragments

- **Given** an uncomposed fragment at release time
- **When** the release gate runs
- **Then** it fails naming the fragment - no entry is silently dropped from a cut
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_changelog.py -k StrayFragment
- **Verified:** yes (2026-07-16)

### AC3: doc-coverage accepts a fragment as the entry

- **Given** a behaviour change whose entry exists only as a fragment
- **When** the changelog-empty check runs
- **Then** the fragment satisfies it; an empty [Unreleased] with no fragments still fails
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_changelog.py -k FragmentCoverage
- **Verified:** yes (2026-07-16)

### AC4: Convention documented

- **Given** a contributor reading the outputs reference
- **When** they look up changelog practice
- **Then** reference-outputs.md documents fragments; direct editing stays valid for non-adopters
- **Verify:** grep "changelog.d" .claude/skills/sdlc-studio/reference-outputs.md
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
