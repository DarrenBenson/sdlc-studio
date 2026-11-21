# BG1399: lane land commits and lands the code, then refuses a self-check missing a required surface, when the builder can no longer be resumed

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_before_commit.py, changelog.d/BG1399.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_resume.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_brief_repair_scope.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: orchestrator
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:11:29Z

## Summary

The commit-message claims check runs after the commit, so the refusal arrives once the worktree and builder have gone.

## Steps to Reproduce

Land a unit whose self-check omits commit-message claims.

## Proposed Fix

Run the self-check gate before the commit.

Further evidence, 2026-11-18 (the website's RUN-01M7R7KN): all three lane builders wrote each
claim's `ruling` as "TRUE: <evidence>" and each mutant's `test` as a vitest command line rather
than `path::name`. The evidence lane landed and committed, then its self-check was refused with
its worktree removed, so the builder was resumed to fix files under `.local/lane/landed/`; the
other two were caught by reading the hand-in before landing. The lane brief describes each file as
`{surface, claim, ruling}` and `{mutant, test, result, answer}` without saying the ruling is one
bare word or the test a `path::name`, so the fix also names the allowed values in the brief.

## Acceptance Criteria

- [ ] **AC1** Given a self-check missing a required surface, when `sprint lane land` runs, then it refuses before committing and leaves the worktree intact. Fails on: the commit made first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_before_commit.py::SelfCheckBeforeCommitTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Affects widened in-run: its refusal before the commit changes the scenario test_lane_land_resume.py's stopped-after-fast-forward case relied on, so that case stops another way |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Affects widened in-run: its refusal before the commit now reaches a repair-brief fixture whose claims omit the changelog fragment, so the fixture gains that claim |
