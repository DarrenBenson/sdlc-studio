# US1225: A verify run in a lane worktree changes no file outside the unit's Affects

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0683
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0334
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A verify run in a lane worktree changes no file outside the unit's Affects
**So that** CR0683 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A verify run in a lane worktree leaves nothing changed outside Affects

- **Given** a builder's lane worktree for a story whose Affects does not name the story file, with the unit's change staged and its verifiers green
- **When** `verify_ac.py run --story <id>` is run in that worktree
- **Then** it exits 0 and `git status --porcelain` lists no path outside the unit's Affects, the story file included. Fails on: a `Verified:` stamp left as an unstaged change to the story file, which each run-seven builder restored by hand
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::LaneWorktreeFootprintTests::test_a_run_in_a_lane_worktree_changes_no_file_outside_affects

### AC2: The lane run's result is still reported and a red criterion still fails

- **Given** the same lane worktree with one criterion whose verifier fails
- **When** `verify_ac.py run --story <id>` is run in it
- **Then** it exits non-zero and names the failing criterion and each passing one, and the tree outside Affects is still unchanged. Fails on: a run that keeps the tree clean by not running the verifiers, or by reporting nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::LaneWorktreeFootprintTests::test_a_red_criterion_in_a_lane_worktree_is_named_and_exits_non_zero

### AC3: A run on the root checkout still stamps the story

- **Given** the same story on the project's root checkout, outside any lane worktree
- **When** `verify_ac.py run --story <id>` is run
- **Then** each passing criterion gains its `Verified:` line in the story file, as before. Fails on: a fix that stops stamping everywhere, so `transition` to Done finds no verified criteria
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::LaneWorktreeFootprintTests::test_a_run_on_the_root_checkout_still_stamps_the_story

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
