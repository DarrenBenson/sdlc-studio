# BG1311: `sprint.py lane land` removes the builder's worktree, so the builder cannot be resumed for a repair after a REJECT and a fresh builder must re-read the unit from cold

> **Status:** Fixed
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, changelog.d/BG1311.md
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

Recreate the worktree at the same path on `lane brief` for a repair, from the land record's path and landed commit, and say so in reference-sprint-toolchain.md. The other option (keep the worktree until `lane accept`) is rejected here: it would change the `remove` step of `LAND_STEPS`, the resume logic and about a dozen tests that assert removal, and `lane accept` and `drive.py` with them, which is an 8-point change; take that route only as a separate unit.

## Acceptance Criteria

- [ ] **AC1** Given a unit built in an isolated worktree, landed with `sprint.py lane land` and then given a REJECT, when its repair is briefed with `sprint.py lane brief --units <id>`, then a worktree exists at the path it was built in, on the landed commit with a clean tree. Fails on: the path being gone after `lane land` (the `remove` step, `LAND_STEPS`), so the original builder cannot be resumed (reproduced by reading `_remove`: it runs `git worktree remove` and `branch -d` unconditionally).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_repair_brief_recreates_the_landed_worktree_at_its_path
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given a unit whose land record is missing or whose original path is occupied, when its repair is briefed, then the brief still prints and names why no worktree was recreated; nothing is overwritten. Fails on: a repair brief that fails or overwrites a directory it did not create.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_repair_brief_with_no_land_record_or_an_occupied_path_still_prints
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given the landing rows of `reference-sprint-toolchain.md`, when read, then they say `lane land` removes the worktree and `lane brief` for a repair recreates it at the same path. Fails on: the runbook silent on how a landed builder is resumed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_the_runbook_says_a_repair_brief_recreates_the_worktree
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced by execution reading (`_remove` at lanes.py line 485 still removes the worktree and branch at the land's `remove` step); chose the smaller recreate-on-brief fix (3 points) over keep-until-accept (8, over the split threshold) and rewrote criteria to match; sprint.py added to Affects for the `lane brief` verb |
