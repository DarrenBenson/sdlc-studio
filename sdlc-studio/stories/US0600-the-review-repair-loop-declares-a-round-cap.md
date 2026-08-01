# US0600: The review-repair loop declares a round cap and the growing-set detector GATES rather than reports, so a diverging loop stops and hands off

> **Status:** Ready
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
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopTerminationTests::test_the_round_cap_ends_the_loop

### AC2: a growing outstanding set GATES rather than reports

- **Given** an outstanding finding set that has grown across two consecutive rounds
- **When** the loop checks its own progress
- **Then** it stops and names the divergence, because a loop that reports it is diverging and continues anyway has reported nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopTerminationTests::test_a_growing_set_stops_the_loop

### AC3: a shrinking set runs on

- **Given** an outstanding set that shrank this round
- **When** the same check runs
- **Then** the loop continues, so termination cannot be satisfied by a gate that stops every loop
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopTerminationTests::test_a_shrinking_set_runs_on

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
