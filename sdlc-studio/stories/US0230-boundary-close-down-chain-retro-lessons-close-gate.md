# US0230: boundary close-down chain (retro + lessons + close gate); halt on a failed gate

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0076
> **Depends on:** US0233
> **Points:** 3

## User Story

**As an** operator whose run continues without me
**I want** each cycle properly closed - retro, lessons, close gate - before the next one is planned
**So that** the next cycle plans on judged, reconciled state instead of inheriting an unclosed sprint

## Acceptance Criteria

### AC1: Run the close-down chain at every boundary

- **Given** a rolling run whose current cycle has finished its batch and more cycles remain
- **When** the boundary is reached
- **Then** the close ceremony runs for that cycle (retro validate and extract, lessons summary, close gate) before any re-plan, and each step is reported against the cycle it closed
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k BoundaryCloseDownTests

### AC2: A failed close gate halts the run

- **Given** a boundary whose close-down chain fails a step (an unfilled retro, an unjudged sprint goal, or a failing gate)
- **When** the rolling loop evaluates that boundary
- **Then** no further cycle is planned or executed, the loop exits non-zero, and the message names the failing step and its remedy
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k BoundaryGateHaltTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
