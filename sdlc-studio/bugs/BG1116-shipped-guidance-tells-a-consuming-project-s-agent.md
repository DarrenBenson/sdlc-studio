# BG1116: Shipped guidance tells a consuming project's agent to run the full suite before every commit, which the shipped gate's per-commit selection and push-boundary suite exist to avoid

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** AGENTS.md, .claude/skills/sdlc-studio/reference-agentic-lessons.md, tools/tests/test_agentic_lessons_full_suite.py, changelog.d/BG1116.md
> **Evidence:** US1090 build, 2026-10-22: the builder's sweep for other full-suite-before-commit instructions.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T06:57:21Z

## Summary

reference-agentic-lessons.md:269, under 'Two habits go with it' (which lists three), says '**Run the full suite before every commit, never a filtered subset.**' The shipped gate selects a commit's test modules from what it changes and runs the whole suite at a boundary (`gate.py --boundary push`); this repository's own rule was reworded to match under D0382 and US1090. A user whose agent follows the lesson pays the full suite on every commit, the per-commit cost D0389 set out to cut. The safety the habit protects is kept by the boundary: no commit leaves the machine without the full suite.

US1090's QA review (APPROVE, round 1, 2026-10-22) found the same subject in AGENTS.md:137: 'the pre-push hook runs the whole suite on each pushed commit' reads as every commit in the push, but the hook judges only the commit each pushed ref points at. Non-blocking there, since US1090's criterion does not cover the sentence.

## Steps to Reproduce

Read reference-agentic-lessons.md lines 267-277.

## Proposed Fix

Restate the habit as: a commit runs the modules its change selects, and the full suite runs before the work leaves the machine (`gate.py --boundary push`, or the project's pre-push hook); never push on a filtered subset. Keep its evidence (17 and 27 failures, which the boundary also catches). Correct 'Two habits' to the count the list holds.

## Acceptance Criteria

- [ ] **AC1** Given the habits list under the post-review lesson, when its bold lead sentences are read from the source as a set, then none tells the reader to run the full suite before every commit, one names the full suite at the push boundary, and the count the lead-in states equals the list's length
  - **Verify:** pytest tools/tests/test_agentic_lessons_full_suite.py::AgenticLessonsFullSuiteTests::test_the_habit_runs_the_full_suite_at_the_boundary
- [ ] **AC2** AGENTS.md's push-gate paragraph says the pre-push hook judges the commit each pushed ref points at, not each pushed commit: the hook collects one commit per stdin ref line (.githooks/pre-push:27-35), so the intermediate commits of a push are not judged by the full suite
  - **Verify:** pytest tools/tests/test_agentic_lessons_full_suite.py::AgenticLessonsFullSuiteTests::test_agents_md_names_the_commit_each_ref_points_at

## Impact

Shipped guidance multiplies a user's commit cost by the full suite's run time on every commit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
| 2026-10-22 | sdlc | AC2 and AGENTS.md added from US1090's QA review: the push-gate paragraph's 'each pushed commit' |
