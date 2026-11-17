# US1262: sprint lane status lists each open lane with its worktree, newest change age and elapsed time against its estimate, marking a stall

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0711
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_status.py
> **Epic:** EP0351
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** sprint lane status lists each open lane with its worktree, newest change age and elapsed time against its estimate, marking a stall
**So that** CR0711 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each open lane is listed with its worktree, newest change and elapsed time

- **Given** a run with two lane worktrees, each for a pointed unit, whose newest changed files are of known ages
- **When** `sprint.py lane status` is run, as text and with `--format json`
- **Then** each lane is listed once with its unit, its worktree path, the age of its newest changed file and its elapsed time beside the estimate its points give, and the JSON form carries the same fields; a unit with no measured minutes per point reads the estimate as not measured, not as zero. Fails on: an open lane missing from the list, or an age read from a file under the worktree's ignored directories instead of the lane's work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_status.py::LaneStatusTests::test_each_open_lane_lists_its_worktree_change_age_and_elapsed_against_estimate

### AC2: A lane with no change past the threshold is marked STALLED

- **Given** one lane whose newest change is older than the stall threshold and one whose newest change is inside it
- **When** `sprint.py lane status` is run, and run again with the threshold raised above the first lane's age
- **Then** the first lane is marked STALLED and the second is not; with the threshold raised neither is marked. Fails on: a lane silent for two hours listed as live, or a threshold that cannot be set
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_status.py::LaneStatusTests::test_a_lane_silent_past_the_threshold_is_marked_stalled

### AC3: No open lane, and a lane that has changed nothing, are both reported

- **Given** a repository with no lane worktree, then one lane worktree in which no file has been changed since it was created
- **When** `sprint.py lane status` is run in each
- **Then** the first run says no lane is open and exits 0; the second lists the lane with its age counted from the worktree's creation, and marks it STALLED once that passes the threshold. Fails on: a traceback on an empty run, or a builder that never wrote a file read as having no age and so never stalled
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_status.py::LaneStatusTests::test_no_open_lane_and_an_untouched_lane_are_reported

### AC4: The runbook and the help page name the step

- **Given** the shipped `help/sprint.md`, `reference-sprint-toolchain.md` and `reference-scripts-surface.md`
- **When** each is read for the lane actions `sprint.py lane --help` lists
- **Then** `status` is among the actions `sprint.py lane` accepts, the help page describes it with its threshold option, and the runbook names `sprint lane status` as the check on a lane in flight. Fails on: an action the parser takes that no page names
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_status.py::LaneStatusDocsTests::test_the_runbook_and_help_name_lane_status

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
