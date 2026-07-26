# US0350: export each lane as a per-team worklist, assert collision-freedom, state the undeclared-file risk

> **Status:** Done
> **Delivers:** CR0321
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0118
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-sprint.md

## User Story

**As a** sprint operator handing lanes to separate teams, agents or worktrees
**I want** each lane exported as a worklist the planner reads back, with collision-freedom asserted on the export
**So that** a team can pick up a lane directly, and the disjointness guarantee - and its limit - travels with the artefact

## Acceptance Criteria

### AC1: each lane exports as a worklist the planner accepts

- **Given** a computed lane partition
- **When** each lane is exported
- **Then** each export is a worklist file `sprint plan --worklist` reads back, and re-planning from it reproduces that lane's units exactly
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneExportTests::test_each_lane_round_trips_through_the_worklist_reader
- **Verified:** yes (2026-07-25)

### AC2: collision-freedom is asserted on the exports, not assumed from the computation

- **Given** the exported worklists
- **When** they are read back and their units' Affects are intersected pairwise
- **Then** every pair is disjoint - the assertion is made against the artefacts handed to teams, not against the in-memory structure that produced them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneExportTests::test_the_exports_themselves_are_pairwise_disjoint
- **Verified:** yes (2026-07-25)

### AC3: the undeclared-file risk is stated where the lanes are handed over

- **Given** an export intended for a separate team, agent or worktree
- **When** a reader opens it
- **Then** it states plainly that disjointness is only as good as the declared `Affects`, and that a unit touching an undeclared file can still collide - the guarantee's limit travels with the artefact
- **Verify:** grep undeclared .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
