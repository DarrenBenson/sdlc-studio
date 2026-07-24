# US0349: sprint plan emits a report-only lane partition from the Affects clusters

> **Status:** Draft
> **Delivers:** CR0321
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0118
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the plan emits a lane partition with no file shared between lanes

- **Given** a batch whose units declare overlapping `Affects`
- **When** `sprint plan` runs
- **Then** it reports lanes such that no file appears in two lanes, computed from the existing Affects-derived clusters rather than a second implementation
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LanePartitionTests::test_no_file_appears_in_two_lanes

### AC2: the partition is report-only and changes no plan decision

- **Given** the same batch
- **When** the plan is produced with and without the partition computed
- **Then** the approved batch, its ordering and its forecast are byte-identical - this slice reports, it does not allocate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LanePartitionTests::test_the_partition_changes_nothing_else_in_the_plan

### AC3: a unit with no declared Affects is named, not silently placed

- **Given** a batch containing a unit that declares no files
- **When** the partition is computed
- **Then** that unit is reported as unplaceable and named, rather than being dropped or put in a lane by default - an undeclared file is invisible to a collision check, so it cannot be assumed safe
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LanePartitionTests::test_an_undeclared_unit_is_named_not_placed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
