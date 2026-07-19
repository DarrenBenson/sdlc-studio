# US0231: fetch and origin-drift check at each boundary, refuse under --strict

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0076
> **Depends on:** US0233
> **Points:** 2

## User Story

**As an** operator on a repo other people also push to
**I want** every cycle boundary to fetch and compare against origin, not just the first plan
**So that** a long unattended run cannot spend hours planning against a checkout the team moved past

## Acceptance Criteria

### AC1: Fetch and compare at every boundary

- **Given** a rolling run of more than one cycle on a repo that has an origin
- **When** each boundary is reached
- **Then** the origin-drift check runs with a fetch at that boundary and reports its result per cycle, and `--no-fetch` suppresses the fetch while still comparing
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k BoundaryOriginFetchTests
- **Verified:** yes (2026-07-19)

### AC2: Divergence refuses under --strict

- **Given** a boundary at which local is behind origin's default branch
- **When** the rolling loop runs under `--strict`
- **Then** it stops at that boundary without planning or executing the next cycle; without `--strict` it prints the drift warning and continues
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k BoundaryStrictDriftRefusalTests
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
