# US0401: a non-done close records tokens with the tokens-per-point blank, and reference-sprint.md notes the rungs differ

> **Status:** Draft
> **Delivers:** CR0407
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0151
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_nondone_close.py

## User Story

**As a** operator closing a run that was driven to a rung short of the build rung
**I want** the velocity row to record the token spend without a tokens-per-point figure
**So that** no partial-rung row contaminates the velocity record the next plan re-measures its rate from

## Acceptance Criteria

### AC1: a non-`done` rung close records tokens with the rate left blank

- **Given** an open run driven to a non-`done` rung (e.g. `design`) whose retro records some terminal units carrying points, and a harness token total
- **When** `accuracy --write` records the velocity row
- **Then** the row carries the token actual with tokens-per-point blank (not tokens divided by the terminal-unit points), so a design-run row cannot be re-measured as a rate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_nondone_close.py::NonDoneCloseLeavesRateBlank::test_design_rung_records_tokens_without_rate

### AC2: a `done` rung close still computes the rate

- **Given** an open run driven to the `done` rung whose delivered units carry points, and a harness token total
- **When** `accuracy --write` records the velocity row
- **Then** tokens-per-point is computed and written as before, so the build rung's measurement is not lost
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_nondone_close.py::NonDoneCloseLeavesRateBlank::test_done_rung_still_computes_rate

### AC3: reference-sprint.md states the rungs cost differently

- **Given** the reference documentation for the sprint forecast
- **When** an operator reads reference-sprint.md
- **Then** it states that the `--goal` rungs cost differently and that only the build (`done`) rung carries a measured rate
- **Verify:** manual confirm reference-sprint.md documents that the forecast rungs cost differently and only the build rung has a measured rate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
