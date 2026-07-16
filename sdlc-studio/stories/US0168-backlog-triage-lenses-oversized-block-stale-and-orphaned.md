# US0168: Backlog-triage lenses: oversized (block), stale, and orphaned-dependency

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/backlog_triage.py
> **Epic:** EP0047
> **Points:** 5

## User Story

**As an** operator about to plan a sprint
**I want** oversized, stale, and orphaned-dependency items surfaced
**So that** the backlog I plan from is correctly sized, current, and its dependencies real

## Acceptance Criteria

### AC1: a delivery unit above the 8-point ceiling blocks; a unit at the ceiling reports; within-ceiling is clean

- **Given** units sized 13, 8, and 5 points
- **When** triage runs
- **Then** the 13 blocks (decompose), the 8 reports (at the ceiling), the 5 is clean
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_backlog_triage.py -k Oversized
- **Verified:** yes (2026-07-16)

### AC2: an old undepended item is stale; a recent or depended-on one is not; a dependency on a terminal/absent artefact is orphaned

- **Given** an old item nothing depends on, a recent item, a depended-on old item, and a dependency on a non-open artefact
- **When** triage runs
- **Then** only the old undepended item is stale, and only the non-open dependency is orphaned
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_backlog_triage.py
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
