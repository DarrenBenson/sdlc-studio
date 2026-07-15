# US0161: retro.py records an actual token count and computes tokens-per-point for an interactive sprint

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Epic:** EP0045
> **Points:** 3

## User Story

**As an** operator closing an interactive sprint
**I want** to supply the harness-tracked token total and get a real tokens-per-point
**So that** an interactive sprint has a deterministic velocity, not a blank.

## Acceptance Criteria

### AC1: accuracy --tokens N yields a real sprint tokens-per-point over the delivered (artefact) points, with no telemetry

- **Given** an interactive sprint (delivered units with Points, no per-unit telemetry)
- **When** `retro.py accuracy --id RETRO --tokens N` runs
- **Then** it computes `sprint_tokens_per_point = N / delivered points` (points read from the artefacts), reports it in the block, leaves per-unit rows honestly UNMEASURED, and reports nothing when no tokens are supplied
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_retro.SprintTokenActualTests
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
