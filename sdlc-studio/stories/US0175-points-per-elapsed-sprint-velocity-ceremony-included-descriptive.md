# US0175: Points-per-elapsed-sprint velocity, ceremony included, descriptive-only and fed to no gate

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Epic:** EP0048
> **Points:** 5

## User Story

**As an** operator planning the next sprint
**I want** a points-per-elapsed-sprint velocity, ceremony included
**So that** I have a human-legible read of what a session delivers

## Acceptance Criteria

### AC1: primary velocity is points/elapsed-hour from the sprint's own run-state or a supplied figure; a stale run-state is ignored; the secondary is worker-time; both descriptive

- **Given** a delivered batch with an operator-supplied elapsed, no elapsed, a stale non-matching run-state, and a matching run-state
- **When** `accuracy` computes velocity
- **Then** the primary is points/elapsed-hour when known and UNMEASURED otherwise; a run-state whose batch is not this sprint's is ignored; the secondary points-per-worker-hour comes from wall-time; none of it feeds a gate
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_retro.py -k Velocity
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
