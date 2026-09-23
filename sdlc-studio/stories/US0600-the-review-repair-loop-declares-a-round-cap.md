# US0600: The review-repair loop declares a round cap and the growing-set detector GATES rather than reports, so a diverging loop stops and hands off

> **Status:** Done
> **Closed with findings in:** repaired in 307ce91d - the close STOPS on divergence; mutant re-run and KILLED
> **Delivers:** CR0514
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0198
> **Points:** 5

## User Story

**As a** operator whose sprint is running unattended
**I want** the review-repair loop to stop when it stops converging
**So that** a loop with no exit cannot burn a night going backwards

## Acceptance Criteria

### AC1: a declared round cap ends the loop

- **Given** a review-repair loop that has reached its declared round cap
- **When** another round would begin
- **Then** it stops and hands off with the state named, because a cap nobody enforces is a comment
- **Verify:** manual - retired by D0259: superseded by US0876, the close runs once and finishes, recording gaps as known issues
- **Verified:** manual (2026-09-24) - retired, superseded by US0876 (D0259)

### AC2: a growing outstanding set GATES rather than reports

- **Given** an outstanding finding set that has grown across two consecutive rounds
- **When** the loop checks its own progress
- **Then** it stops and names the divergence, because a loop that reports it is diverging and continues anyway has reported nothing
- **Verify:** manual - retired by D0259: superseded by US0876, the close runs once and finishes, recording gaps as known issues
- **Verified:** manual (2026-09-24) - retired, superseded by US0876 (D0259)

### AC3: a shrinking set runs on

- **Given** an outstanding set that shrank this round
- **When** the same check runs
- **Then** the loop continues, so termination cannot be satisfied by a gate that stops every loop
- **Verify:** manual - retired by D0259: superseded by US0876, the close runs once and finishes, recording gaps as known issues
- **Verified:** manual (2026-09-24) - retired, superseded by US0876 (D0259)

### AC4: one round of growth alone does not stop the loop

- **Given** a round that surfaced more than it fixed, followed by one that converged
- **When** the rule runs
- **Then** the loop continues, because a repair exposing its neighbour is ordinary (LL0052) and only two consecutive growing rounds mean a moving target
- **Verify:** manual - retired by D0259: superseded by US0876, the close runs once and finishes, recording gaps as known issues
- **Verified:** manual (2026-09-24) - retired, superseded by US0876 (D0259)

### AC5: the rule is consulted by the close, not only importable

- **Given** the shipped `_record_close_attempt`
- **When** it is read
- **Then** it calls the termination rule AND acts on it, because a rule reachable only from Python is the lane-not-library defect (LL0040)
- **Verify:** manual - retired by D0259: superseded by US0876, the close runs once and finishes, recording gaps as known issues
- **Verified:** manual (2026-09-24) - retired, superseded by US0876 (D0259)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
