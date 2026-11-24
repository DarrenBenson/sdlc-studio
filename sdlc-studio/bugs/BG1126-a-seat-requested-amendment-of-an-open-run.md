# BG1126: A seat-requested amendment of an open run's goal leaves the run state on the old goal, so the close's goal read reports 'a different goal'

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/BG1126.md
> **Evidence:** US1096 QA review round 1, qa-seat-US1096-r1, at 7f113429: pre-existing finding, reproduced at e877a6b9.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T15:07:16Z

## Summary

US1096's QA review (round 1, 2026-10-22), pre-existing at e877a6b9. US1096 moves an open run's goal only for an amendment recorded with `--requested-by operator`. An amendment recorded with `--requesting-seat <role>` on an open run records the new wording on the goal-review round but leaves the run state's `sprint_goal` on the planned wording, so the close's goal read compares against the old goal and reports the reviewed one as a different goal.

Reproduced at cecc9dfe7 (2026-11-24) on `test_goal_review_one_round.py`'s `run` fixture (a run opened on G): `goal-review record --goal G2 --amend-from G --requesting-seat qa` exits 0 and records round 2 on G2, the run state's `sprint_goal` stays G, and `close_goal_judgement` judges the clause G (`UNANSWERED (4 seat(s) silent): ship the parser to users`). In `cmd_goal_review` only `if by_operator:` calls `_run_goal_to_amend`. reference-sprint.md says only an operator's amendment moves an open run's goal.

## Steps to Reproduce

Open a run with goal G; record `sprint.py goal-review record --goal G2 --amend-from G --requesting-seat qa ...`; run the close's goal read: it judges G and names G2 as different.

## Proposed Fix

Apply US1096's open-run move to a seat-requested amendment too, with the same guards (the open run's goal, no goal verdict yet, the word limit), recording the requesting seat on the `sprint_goal_amendments` entry rather than `operator`. Say so in reference-sprint.md's amend paragraph.

## Acceptance Criteria

- [ ] **AC1** Given a run opened on goal G with every seat's verdict recorded on G, when `goal-review record --goal G2 --amend-from G --requesting-seat qa` runs, then the run state's `sprint_goal` is G2, its `sprint_goal_amendments` entry records G to G2 with the qa seat as the requester (not `operator`), and `close_goal_judgement` judges G2 and not G. Fails on: the run state left on G, so the close judges the wording the amendment replaced.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::SeatAmendOpenRunTests::test_a_seat_requested_amendment_moves_the_goal_the_close_judges
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given the same run after its goal verdict is recorded, when a seat-requested amendment of G is recorded, then it exits 2 naming that verdict and neither goal-review.json nor run-state.json changes. Fails on: rc 0 with a round recorded on G2 while the run's judged goal stays G.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::SeatAmendOpenRunTests::test_a_seat_requested_amendment_after_the_goal_verdict_is_refused
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given an open run whose goal is G and a seat-requested amendment from another reviewed goal, or a closed run on G, when the amendment is recorded, then run-state.json is byte for byte unchanged. Fails on: a mutant moving the run's goal to whatever `--amend-from` names, or moving a closed run's goal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::SeatAmendOpenRunTests::test_a_seat_requested_amendment_leaves_another_or_a_closed_run_alone
  - **Verified:** yes (2026-11-24)

## Impact

A goal improved at a seat's request mid-run is judged at the close against the wording it replaced.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe7; the move chosen over the refusal; three executable criteria (the move, the verdict guard, the other-goal and closed-run guard); Affects drops test_sprint.py and adds reference-sprint.md; Points 2 to 1 |
