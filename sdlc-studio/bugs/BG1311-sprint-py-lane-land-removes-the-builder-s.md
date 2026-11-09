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

- [ ] **AC1** The behaviour described is corrected: Hit in run nine on 2026-11-09: US1143 landed (lane land removed its worktree and branch), was REJECTED at QA round 1, and resuming its original builder for the...
- [ ] **AC2** The proposed fix lands, pinned by a test: Keep the landed worktree (reset to the landed commit) until the unit is accepted, or recreate it at the same path on `lane brief` for a repair, and say in...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
