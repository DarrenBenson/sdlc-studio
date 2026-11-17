# BG1311: `sprint.py lane land` removes the builder's worktree, so the builder cannot be resumed for a repair after a REJECT and a fresh builder must re-read the unit from cold

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md
> **Evidence:** RUN-01M7061X, US1143's repair, 2026-11-09: the SendMessage resume refusal
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T13:54:18Z

## Summary

Hit in run nine on 2026-11-09: US1143 landed (lane land removed its worktree and branch), was REJECTED at QA round 1, and resuming its original builder for the repair failed with 'its worktree no longer exists, and the fallback directory is not covered by the session's isolation fences'. The efficiency practice the run follows (resume the original builder for a repair rather than brief a fresh one, D0404's lessons) cannot apply to any unit that has landed, which is every unit a reviewer sees, so each repair pays a fresh builder's cold read of the brief, the files and the verdict.

## Steps to Reproduce

1. Build a unit in an isolated worktree and land it with `sprint.py lane land --worktree <path> --units <id>`.
2. Record a REJECT for it.
3. Try to resume the same builder agent for the repair: the harness refuses because the worktree is gone.

## Proposed Fix

Keep the landed worktree (reset to the landed commit) until the unit is accepted, or recreate it at the same path on `lane brief` for a repair, and say in reference-sprint-toolchain.md which; add a test that a landed unit's worktree path exists until `lane accept` APPROVEs it.

## Acceptance Criteria

- [ ] **AC1** Given a unit built in an isolated worktree, landed with `sprint.py lane land` and then given a REJECT, when its repair is briefed with `sprint.py lane brief --units <id>`, then the builder's worktree exists at the path it was built in, on the landed commit with a clean tree. Fails on: the path being gone, so the original builder cannot be resumed and a fresh one reads the unit from cold.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_landed_units_worktree_is_there_for_its_repair_after_a_reject
- [ ] **AC2** Given a landed unit whose review is an APPROVE, when `sprint.py lane accept` accepts it, then its worktree and its branch are removed. Fails on: accepted lanes leaving their worktrees behind for the rest of the run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_an_accepted_units_worktree_and_branch_are_removed
- [ ] **AC3** Given the landing row of `reference-sprint-toolchain.md`, when it is read, then it says the landed worktree is available for a repair until the unit is accepted, and names the command that removes it. Fails on: the runbook still saying `lane land` removes the worktree.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_the_runbook_says_when_a_landed_worktree_is_removed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
