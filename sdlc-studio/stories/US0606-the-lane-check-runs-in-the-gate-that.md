# US0606: The lane-check runs in the gate that already runs verify_ac, reporting only, with its yield accumulated where a blocking decision can read it

> **Status:** Done
> **Closed with findings in:** repaired in 307ce91d (stale yield figure); residue in BG0493
> **Delivers:** CR0520
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0199
> **Points:** 3

## User Story

**As a** maintainer deciding whether the check may block
**I want** the lane-check running in the gate with its yield accumulated
**So that** the blocking decision rests on a measured number rather than an assertion

## Acceptance Criteria

### AC1: the pass runs in the gate that already runs verify_ac

- **Given** a commit touching a CLI-bearing script
- **When** the gate runs
- **Then** the lane-check runs with it and reports on a channel that cannot fail the commit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::LaneCheckLaneTests::test_the_lane_runs_and_does_not_block
- **Verified:** yes (2026-08-02)

### AC2: its yield accumulates where a decision can read it

- **Given** several runs of the lane
- **When** the accumulator is read
- **Then** it carries runs and findings under `sdlc-studio/.local/`, never a tracked path the hook does not stage
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::LaneCheckLaneTests::test_the_yield_accumulates_under_local
- **Verified:** yes (2026-08-02)

### AC3: the pass is reachable through its own command

- **Given** `verify_ac.py lane-check`
- **When** it is invoked through the CLI
- **Then** it reports and exits zero, because this unit's other criteria assert on the hook's text and would stay green with the subcommand broken - a gap the lane-check itself reported against this very unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::LaneCheckLaneTests::test_the_pass_runs_through_its_own_command
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
