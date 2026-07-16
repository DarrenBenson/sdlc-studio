# US0180: flow compute: per-unit cycle time, weekly throughput and work-item age from census + git log

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py, .claude/skills/sdlc-studio/reference-scripts.md
> **Epic:** EP0052
> **Points:** 5

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** a zero-token flow instrument: cycle time, throughput and work-item age computed from the artefact census and git log
**So that** I can see how work actually flows without burning tokens on narrated status

## Acceptance Criteria

### AC1: Per-unit cycle time from Created to terminal

- **Given** a workspace with delivered units whose files carry Created dates and git history
- **When** flow compute runs
- **Then** each terminal unit reports cycle time in days derived from its Created date and its terminal transition commit, pure stdlib
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_flow.py -k CycleTime
- **Verified:** yes (2026-07-16)

### AC2: Weekly throughput from terminal dates

- **Given** the same workspace
- **When** flow compute runs
- **Then** throughput is reported as units per week over a stated window
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_flow.py -k Throughput
- **Verified:** yes (2026-07-16)

### AC3: Work-item age for every non-terminal unit

- **Given** units in Draft/Ready/In Progress
- **When** flow compute runs
- **Then** each non-terminal unit reports its age since Created; nothing is guessed for units missing a date - they are named as unmeasurable
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_flow.py -k Age
- **Verified:** yes (2026-07-16)

### AC4: The new script is catalogued

- **Given** a reader of the scripts catalogue
- **When** they look for flow
- **Then** reference-scripts.md carries the flow.py row
- **Verify:** grep "flow.py" .claude/skills/sdlc-studio/reference-scripts.md
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
