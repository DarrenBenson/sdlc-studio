# US0279: An interactive close captures the harness-tracked token total into the velocity row without hand entry

> **Status:** Draft
> **Delivers:** CR0350
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0091
> **Depends on:** BG0218
> **Points:** 3

## User Story

**As a** sprint operator
**I want** an interactive close to record its token actuals by itself
**So that** estimate-versus-actual closes for interactive runs as it does for runner ones

## Acceptance Criteria

### AC1: an interactive close captures the harness-tracked token total

- **Given** an interactive run reaching its close ceremony
- **When** the close completes
- **Then** the harness-tracked token total is captured without the operator supplying it by
  hand, or the close states plainly that it could not and why
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_interactive_close_captures_token_actuals

### AC2: the velocity row records the actual

- **Given** a closed interactive run with a captured token total
- **When** the velocity row is written
- **Then** it records the actual beside the forecast, so the tokens-per-point rate can
  calibrate instead of staying the shipped seed for ever
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py -k test_velocity_row_records_interactive_token_actual

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
