# US0165: Gate grows a bound close-owed lane under --require-close (the soft nudge lives on status/hint)

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Epic:** EP0046
> **Points:** 5

## User Story

**As an** operator gating a push or release
**I want** a blocking gate lane that refuses when a sprint close is owed
**So that** the un-skippable enforcement lands where shipping actually happens

## Acceptance Criteria

### AC1: --require-close binds a blocking close-owed lane that fails on an owed close and passes once a retro covers it

- **Given** a baselined project with an owed close
- **When** `gate --require-close` runs
- **Then** the gate fails; once a retro's `Batch` names the unit, it passes
- **Verify:** manual - retired by US0942: `gate --require-close` and its `close-owed` lane were deleted; the flag now exits 2 naming its retirement
- **Verified:** manual (2026-09-25) - retired, superseded by US0942

### AC2: the close-owed lane is bound-only - never part of the plain gate, and deselecting it under the mode is refused

- **Given** the same project
- **When** a plain `gate` runs (no `--require-close`), or `--require-close --skip close-owed` is attempted
- **Then** the plain gate carries no `close-owed` check, and deselecting the bound lane is refused
- **Verify:** manual - retired by US0942: the bound `close-owed` lane no longer exists, so there is no mode to bind it or deselect it under
- **Verified:** manual (2026-09-25) - retired, superseded by US0942

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Claude Opus 5.5 | AC1, AC2 retired by US0942 (D0259 pattern): `gate --require-close` and the bound `close-owed` lane were deleted; the owed close stays on the `status`/`hint` advisory |
