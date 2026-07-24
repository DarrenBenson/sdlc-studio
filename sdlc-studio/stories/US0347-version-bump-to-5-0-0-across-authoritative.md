# US0347: version bump to 5.0.0 across authoritative files, check_versions --strict green

> **Status:** Ready
> **Delivers:** CR0319
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0117
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/SKILL.md, package.json, CHANGELOG.md, tools/check_versions.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: every authoritative file states 5.0.0

- **Given** the version strings check_versions.py treats as authoritative
- **When** `check_versions.py --strict` is run on a clean tree and its reported version is read
- **Then** it exits 0 AND reports 5.0.0. Asserting only that the guard is green is vacuous: it was green at 4.1.0 and would be green at any consistent version, so the check must bind the VALUE, not the consistency
- **Verify:** shell python3 tools/check_versions.py --strict | grep -q '5\.0\.0'
- **Verified:** no (2026-07-24)

### AC2: the bump is refused while any file disagrees

- **Given** a tree where one authoritative file still reads the old version
- **When** `check_versions.py --strict` is run
- **Then** it exits non-zero and NAMES the disagreeing file, rather than reporting a generic mismatch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/../../../../tools/tests/test_check_versions.py::StrictBumpTests::test_a_single_stale_file_is_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
