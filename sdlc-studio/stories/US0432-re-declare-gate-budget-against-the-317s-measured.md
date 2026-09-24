# US0432: re-declare gate_budget against the ~317s measured peak so a normal commit is under budget and a regression still flags

> **Status:** Done
> **Delivers:** CR0420
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/.config.yaml, tools/tests/test_gate_timing.py
> **Epic:** EP0161
> **Points:** 2

## User Story

**As a** committer on this repo
**I want** the gate-budget ceiling re-declared against the measured gate cost
**So that** a normal commit no longer prints OVER on every run, while a genuine regression still flags

## Acceptance Criteria

### AC1: the declared budget covers the measured cost

- **Given** the re-declared `gate_budget` block in `.config.yaml`
- **When** its ceiling and baseline are read
- **Then** the ceiling covers a baseline that reflects the current ~317s suite (not the pre-growth ~99s that made it fire OVER), so a normal run reads under budget
- **Verify:** manual - retired by US0880: `gate_timing.py budget` and its per-commit ratchet are deleted, and the commit hook reports elapsed time against 90 seconds instead
- **Verified:** manual (2026-09-24) - retired, superseded by US0880

### AC2: a regression above the new budget still flags

- **Given** the re-declared budget
- **When** a run exceeds the new ceiling
- **Then** it still reports OVER, with the drift measured from the new baseline - re-budgeting must not silence the instrument
- **Verify:** manual - retired by US0880: `gate_timing.py budget` and its per-commit ratchet are deleted, and the commit hook reports elapsed time against 90 seconds instead
- **Verified:** manual (2026-09-24) - retired, superseded by US0880

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
