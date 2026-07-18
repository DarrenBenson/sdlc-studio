# US0237: cascade parent epics/CRs/RFCs terminal, write the velocity row, final reconcile

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0077
> **Points:** 5

## User Story

**As an** operator closing a sprint
**I want** the apply-signoff tail to derive parents terminal, write the velocity row, and reconcile
**So that** a closed sprint leaves its epics/CRs terminal and its velocity recorded without a forgotten manual `retro accuracy --write`

## Acceptance Criteria

### AC1: the tail writes a velocity row for the run's retro

- **Given** a batch whose story units were just transitioned Done by `--apply-signoff`
- **When** the apply-signoff tail runs
- **Then** a velocity row keyed by the run's retro id is written to `retros/VELOCITY.md` (upserted, not duplicated)
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_sprint.ApplySignoffTailTests
- **Verified:** yes (2026-07-18)

### AC2: parent epics/CRs whose children are all terminal derive terminal, and a final reconcile leaves drift 0

- **Given** the story units of an epic are all Done after the fan
- **When** the tail's cascade + final reconcile run
- **Then** the parent epic derives terminal and `reconcile detect` reports zero drift
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_sprint.ApplySignoffTailTests.test_ApplySignoffTail_final_reconcile_drift_fails
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
