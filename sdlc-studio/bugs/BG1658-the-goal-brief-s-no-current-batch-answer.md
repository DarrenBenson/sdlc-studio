# BG1658: The goal brief's no-current-batch answer names a goal-review flag that does not exist, and two of US1036's framing branches have no test

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_per_seat.py, changelog.d/BG1658.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T07:37:22Z

## Summary

US1036's engineering second seat (verdict sdlc-studio/reviews/verdicts/US1036/dcfb579577ef-5f9f68ae.txt, RUN-01M7VNR0). The NO CURRENT BATCH TO BRIEF answer (`_seat_brief_body`, now sprint.py:13776) tells the operator to run goal-review brief --worklist, but goal-review accepts only --brief-worklist, so following the advice is an argparse error. The text dates from BG0277. Also unpinned: a seat brief must open with its seat framing (a mutant moving the framing to the end survives), and an unknown seat with no plan written (a mutant there survives). The US1036 commit message overstates what the no-PRD test asserts; that is history and no change here answers it.

Reproduced at cecc9dfe7 (2026-11-24): `sprint.py goal-review brief --worklist x` exits with `error: unrecognized arguments: --worklist x`. In a throwaway copy, two mutants of `seat_brief` survive all six tests of test_goal_review_brief_per_seat.py and the seven other goal-review brief modules: (1) the seat framing appended after the body instead of opening it; (2) `persona_resolve.review_card` called after the stale-plan check, so an unknown seat with no plan gets the NO CURRENT BATCH answer with exit 0 instead of the refusal the docstring promises ("raises its UnknownSeat before any brief is composed").

## Steps to Reproduce

With a stale plan, run sprint.py goal-review brief: the answer says goal-review brief --worklist <file>. Run that: argparse refuses --worklist. Run goal-review --help: only --brief-worklist is listed.

## Proposed Fix

Name `--brief-worklist` in the answer and pin it with a test that runs the named command; add tests that the framing opens a seat brief and that an unknown seat is refused with no plan written.

## Acceptance Criteria

- [ ] **AC1** Given a project with no current plan, when `goal-review brief` answers `NO CURRENT BATCH TO BRIEF`, then the command the answer names, run as written with a worklist file in place of `<file>`, exits 0 and prints a brief. Fails on: the answer naming `--worklist`, which argparse refuses as an unrecognised argument.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_per_seat.py::GoalReviewSeatBriefTests::test_the_stale_plan_answer_names_a_command_that_runs
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given the fixture's worklist and goal, when `goal-review brief --seat qa` runs, then the first line of its output is `You are the qa review seat. Read and adopt the charter at`, and the unframed brief (the control) does not open with it. Fails on: a mutant appending the framing after the body surviving every test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_per_seat.py::GoalReviewSeatBriefTests::test_a_framed_brief_opens_with_its_seat
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given a project with no plan written and no worklist, when `goal-review brief --seat security` names a seat no card fills, then it exits 2 naming the roster, prints nothing on stdout and writes no plan; `--seat qa` there (the control) gives the NO CURRENT BATCH answer with exit 0. Fails on: a mutant resolving the card after the stale-plan check, which answers the unknown seat with exit 0.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_per_seat.py::GoalReviewSeatBriefTests::test_an_unknown_seat_with_no_plan_is_refused
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced the argparse refusal and both surviving mutants at cecc9dfe7; three executable criteria; Affects drops test_sprint.py and adds changelog.d/BG1658.md; Points 2 to 1 |
