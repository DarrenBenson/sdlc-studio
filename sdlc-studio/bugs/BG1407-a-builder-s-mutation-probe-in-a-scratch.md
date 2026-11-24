# BG1407: A builder's mutation probe in a scratch copy of the tests runs without the repo-root conftest.py, so without HOME confinement

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, changelog.d/BG1407.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane accept builder
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:12:34Z

## Summary

The author self-check (`critic.author_self_check`, carried into every lane brief) sends a mutant
the mutation runner cannot run to `MUTANTS.json` with its result, so the builder runs that mutant
by hand, and nothing says where. Run from a copy of the tests alone, the probe runs without the
repository-root `conftest.py`, so without its HOME confinement, and can write the operator's real
home (BG1300's class).

Since this was filed, `mutation.py run --edits` (US1200, 401cc4645) has become the brief's main
route: it copies the whole git work tree, `conftest.py` included, so a runner-driven probe is
confined. Only the hand route is left open.

## Steps to Reproduce

1. Print the author self-check for a unit with a test file in its Affects
   (`critic.author_self_check(root, unit)`): the hand route reads `A mutant the runner cannot run
   goes in MUTANTS.json as {mutant, test, result, answer}` and names no place to run it.
2. Run a test that prints `HOME` from a bare copy of the test file, and from the runner's scratch
   copy (`mutation._copy_work_tree`).

Measured at HEAD 3791e5193: the bare copy sees the operator's real home; the runner's copy
carries `conftest.py` and sees the confined `sdlc-tests-*/home`.

## Proposed Fix

Extend the hand-route sentence in `critic.author_self_check` to say: run such a mutant in the
lane's own worktree or a detached worktree of the repository (`git worktree add --detach`),
never in a copy of the tests alone, so the project's own test configuration (a root
`conftest.py`) applies. Keep it on a line `sprint._hand_in_self_check` passes through, so the
lane brief carries it.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose Affects declare a test file, when its author self-check is printed, then the sentence sending a mutant the runner cannot run to MUTANTS.json also says to run it in the lane's worktree or a detached worktree of the repository, never a copy of the tests alone. Fails on: HEAD, whose sentence names no place (measured: a bare copy's probe sees the operator's real HOME).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::AuthorStepsTests::test_a_mutant_the_runner_cannot_run_is_sent_to_a_worktree
  - **Verified:** yes (2026-11-23)
- [ ] **AC2** Given the lane brief `sprint lane` prints for the same unit, then the hand-in instruction for MUTANTS.json carries the same where-to-run sentence. Fails on: a fix that puts the sentence on a line naming `self-check record`, which `_hand_in_self_check` replaces, so the brief drops it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_the_brief_says_where_a_hand_run_mutant_runs
  - **Verified:** yes (2026-11-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-23 | Sam Eriksson (qa) | Groomed for run twenty-four: the runner route (US1200) now copies `conftest.py` and confines HOME (measured), so the defect narrows to the hand route for a mutant the runner cannot run; the Verify on a module that does not exist replaced by two executable criteria; Affects moves from the builder template to critic.py and the two brief tests; 2 to 1 point |
