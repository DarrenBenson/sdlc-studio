# US0163: Close-owed detector: terminal delivery units since the last retro no retro Batch names

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py
> **Epic:** EP0046
> **Points:** 5

## User Story

**As an** operator running disciplined sprints
**I want** a deterministic answer to "is a sprint close owed right now?"
**So that** a skipped close-down is detectable instead of silently lapsing until the lessons stop compounding

## Acceptance Criteria

### AC1: An uncovered terminal unit newer than the baseline is owed; a covered or grandfathered one is not

- **Given** a project with a stamped `.close-owed-baseline.json` and a delivery unit that reached
  terminal after the baseline with no retro `Batch` naming it
- **When** `close_owed.py detect` runs
- **Then** the unit is reported owed and the command exits non-zero; a unit named by a retro, or
  one below the baseline cutoff, is not owed
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_close_owed.py
- **Verified:** yes (2026-07-16)

### AC2: An unbaselined project reports the tail but never fails

- **Given** a project with uncovered terminal units and no baseline stamped
- **When** `close_owed.py detect` runs
- **Then** it lists the units and asks the operator to baseline first, exiting 0 (a soft state, not a gate failure)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_close_owed.py
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
