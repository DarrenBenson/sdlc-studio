# US0238: idempotent re-run after a mid-cascade stop

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0077
> **Points:** 3

## User Story

**As an** operator whose apply-signoff stopped mid-cascade
**I want** re-running it to resume, not double-count
**So that** a stop (a red unit, an interrupted run) is recovered by simply re-running the same command

## Acceptance Criteria

### AC1: a re-run skips units already Done and signed off

- **Given** `--apply-signoff` stopped partway (some units Done+signed, one refused)
- **When** the same command is re-run after the refusal is resolved
- **Then** already-Done+signed units are skipped (no duplicate sign-off row that changes the latest verdict, no re-transition), and the remaining units complete
- **Verify:** `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k ApplySignoffIdempotent`

### AC2: the tail is idempotent - no duplicate velocity row, no double telemetry

- **Given** a completed `--apply-signoff` re-run against the same run
- **When** it runs a second time
- **Then** the velocity row is upserted (one row per retro id) and an idempotent re-close records no second terminal telemetry event
- **Verify:** `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k ApplySignoffIdempotent`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
