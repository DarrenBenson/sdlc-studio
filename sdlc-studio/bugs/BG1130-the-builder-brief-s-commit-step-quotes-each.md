# BG1130: The builder brief's commit step quotes each Affects path with shlex.quote, but no test has a path with a space, so dropping the quoting stages the wrong paths with every test green

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, changelog.d/BG1130.md
> **Evidence:** US1093 QA review, qa-seat-US1093-r1, 2026-10-26, at ed8cf5e9: new finding 1, the one surviving mutant.
> **Created:** 2026-10-26
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-26T12:21:37Z

## Summary

US1093's QA review (APPROVE, 2026-10-26). `sdlc_md.affects_files` returns a path with a space (`docs/my file.md`), and `lane brief` prints `git add -- <paths>` with each path through `shlex.quote` (sprint.py:2788). Removing the quoting leaves all six tests in `test_lane_builder_brief.py` green, so AC1's 'stages exactly those paths' is untested at that edge.

## Steps to Reproduce

Remove `shlex.quote` at sprint.py:2788 and run tests/`test_lane_builder_brief.py`: green.

## Proposed Fix

Add a spaced path to AC1's fixture and assert the printed `git add` line, split by shlex, equals the Affects list.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose Affects holds a path with a space, when its builder brief is printed, then the commit step's `git add` line, split by shlex, equals the Affects list
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_a_spaced_affects_path_is_staged_whole

## Impact

A builder following the brief on a project with a spaced path would stage the wrong files.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-26 | Claude Opus 5.5 | Filed |
