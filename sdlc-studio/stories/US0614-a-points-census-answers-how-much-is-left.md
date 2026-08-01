# US0614: A points census answers how much is left by status and by type, so the routine question is not answered by a script written on the spot

> **Status:** Ready
> **Delivers:** CR0516
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Epic:** EP0203
> **Points:** 5

## User Story

**As a** operator asking how much is left
**I want** a points census answered by the tooling
**So that** the routine question does not get answered by a script written on the spot

## Acceptance Criteria

### AC1: the census reports points by status and by type

- **Given** a repo with open bugs and Ready stories
- **When** the census runs
- **Then** it reports points totalled by status and by type, not just counts
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::PointsCensusTests::test_points_are_reported_by_status_and_type

### AC2: a terminal unit is excluded

- **Given** a backlog containing a `Won't Implement` story
- **When** the census runs
- **Then** it is excluded, because the first hand-written census silently counted one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::PointsCensusTests::test_a_terminal_unit_is_excluded

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
