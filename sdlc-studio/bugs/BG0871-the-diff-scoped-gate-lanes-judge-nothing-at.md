# BG0871: The diff-scoped gate lanes judge nothing at the push boundary, because their scope is the working-tree diff, which is empty on a clean pushed commit

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py,.claude/skills/sdlc-studio/scripts/tests/test_gate.py,changelog.d/BG0871.md
> **Evidence:** BG0837 QA review, RUN-01M3VF2J, 2026-10-01; gate.py:310
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T11:21:53Z

## Summary

Found by BG0837's QA review (RUN-01M3VF2J): at the push boundary the conformance and validate lanes report '0 of 978 (this diff)'. Their scope is `git diff HEAD` plus untracked files (gate.py:310), so on the clean worktree the pre-push hook now checks out - and, before BG0837, on any clean tree - they never judge the commits being pushed. The full suite still runs, but these two lanes certify nothing about the push.

## Steps to Reproduce

Run the pre-push gate on a clean tree whose pushed commits change an artefact: conformance and validate report 0 units in scope.

## Proposed Fix

At the push boundary scope the diff lanes to the pushed range (the remote ref's sha to the pushed sha) rather than to the working tree, so they judge exactly what is being pushed.

## Acceptance Criteria

- [ ] **AC1** Given a fixture whose pushed commit adds an artefact with a validation error and a clean working tree, when the gate runs at the push boundary for that range, then validate judges that artefact and fails. Fails on: the current scope, which judges 0 units on a clean tree
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::PushBoundaryScopeTests::test_the_diff_lanes_judge_the_pushed_range

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
