# US1256: sprint lane rebase replays a lane's staged work onto main and stops on a conflict with the work intact and the files named

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0707
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_rebase.py
> **Epic:** EP0347
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** sprint lane rebase replays a lane's staged work onto main and stops on a conflict with the work intact and the files named
**So that** CR0707 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A clean replay leaves the same change staged on main's tip

- **Given** a lane worktree holding a staged, uncommitted change, and a main that has gained a commit touching other files
- **When** `sprint.py lane rebase --worktree <path>` is run
- **Then** it exits 0, the worktree's HEAD is main's tip, the staged diff against that HEAD is the change the lane staged, nothing is left unstaged, and no stash entry made by the command remains. Fails on: a worktree still on its old base, staged work that came back unstaged, or a leftover stash
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_rebase.py::LaneRebaseTests::test_a_clean_replay_leaves_the_same_change_staged_on_mains_tip

### AC2: A conflict stops with the staged work recoverable and the files named

- **Given** a lane worktree whose staged change edits a line that a new commit on main also edits
- **When** `sprint.py lane rebase --worktree <path>` is run
- **Then** it exits non-zero, names each conflicting file, names where the lane's staged work is kept, and that kept copy still holds every staged file byte for byte; running the command a second time does not drop or overwrite it. Fails on: the saved work dropped after a failed apply (run thirteen's slip, recovered only by a commit id), or a refusal that names no file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_rebase.py::LaneRebaseTests::test_a_conflict_keeps_the_staged_work_and_names_the_files

### AC3: A worktree it cannot replay safely is refused untouched

- **Given** three worktrees: one with an unstaged edit beside its staged change, one path that is not a worktree of this repository, and one already on main's tip with a staged change
- **When** `sprint.py lane rebase --worktree <path>` is run on each
- **Then** the first two are refused with the reason and their files, index and HEAD are as they were; the third exits 0 saying there is nothing to replay and its staged change is untouched. Fails on: an unstaged edit swept into the replay or lost, or a worktree already current being rewritten
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_rebase.py::LaneRebaseRefusalTests::test_an_unsafe_worktree_is_refused_and_a_current_one_is_left_alone

### AC4: The runbook and the help page name the step

- **Given** the shipped `help/sprint.md`, `reference-sprint-toolchain.md` and `reference-scripts-surface.md`
- **When** each is read for the lane actions `sprint.py lane --help` lists
- **Then** `rebase` is among the actions `sprint.py lane` accepts, the help page describes it with its `--worktree` flag, and the runbook's row for a lane waiting on a moved main names `sprint lane rebase` instead of a hand-run stash. Fails on: an action the parser takes that no page names, or a runbook that still tells the orchestrator to stash by hand
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_rebase.py::LaneRebaseDocsTests::test_the_runbook_and_help_name_lane_rebase

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
