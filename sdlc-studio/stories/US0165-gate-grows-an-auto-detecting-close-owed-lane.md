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
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_gate.py -k CloseOwed
- **Verified:** yes (2026-07-16)

### AC2: the close-owed lane is bound-only - never part of the plain gate, and deselecting it under the mode is refused

- **Given** the same project
- **When** a plain `gate` runs (no `--require-close`), or `--require-close --skip close-owed` is attempted
- **Then** the plain gate carries no `close-owed` check, and deselecting the bound lane is refused
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_gate.py
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
