# US0185: gate lane measures a delivered unit's diff size vs configured thresholds, warn-only, default off

> **Status:** Draft
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/reference-agentic-lessons.md
> **Epic:** EP0055
> **Points:** 3

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** an advisory gate lane that flags a delivered unit whose diff is an outlier for its points
**So that** the AI batch-size failure mode is visible at review time without blocking legitimate large sweeps

## Acceptance Criteria

### AC1: Diff size measured per delivered unit

- **Given** a delivered unit whose commits are identifiable and thresholds configured
- **When** the gate lane runs
- **Then** lines-changed and files-touched are measured and compared to the thresholds; the lane is off until thresholds are set
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_gate.py -k BatchSize

### AC2: Warn-only, fully named

- **Given** a unit over threshold
- **When** the lane fires
- **Then** the warning names the unit, its points, the measured size and the threshold, and states it is advisory - the gate never hard-fails on it
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_gate.py -k BatchWarn

### AC3: Rationale documented

- **Given** a reader of the agentic lessons reference
- **When** they look up the lane
- **Then** the AI batch-size amplification evidence and the never-hard-fails contract are recorded
- **Verify:** grep "batch" .claude/skills/sdlc-studio/reference-agentic-lessons.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
