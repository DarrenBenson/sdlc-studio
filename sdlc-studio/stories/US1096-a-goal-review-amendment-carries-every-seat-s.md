# US1096: A goal-review amendment carries every seat's verdict forward unless a seat asked to re-review, and an amendment of an open run's goal moves the goal the close judges

> **Status:** Ready
> **Delivers:** CR0651
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/US1096.md
> **Epic:** EP0292
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, approving a sprint goal once and then leaving the loop to run
**I want** one goal-review round by default, an amendment recorded without another round of three seats unless a seat asked for one, and an amendment I make to an open run's goal to be the goal the close judges
**So that** the goal review costs one round rather than two to four, and a run reshaped mid-flight is judged on the goal it now has

## Acceptance Criteria

- **AC1:** Given a round with engineering, product and qa verdicts on goal G, when `sprint.py goal-review record --goal G2 --amend-from G --requesting-seat qa` runs with no `--seat`, then the new round carries all three verdicts from G, `goal_review_status(root, G2)` reads reviewed with `needs_reconsult` empty, and `sprint.py plan --sprint-goal G2` prints no seat as owing a verdict
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::OneRoundTests::test_an_amendment_carries_every_verdict_forward
- **AC2:** Given qa's verdict on G recorded with `rereview: yes` (a `--fields-file` seat key, and a sixth field of the `--seat` form), when the amendment is recorded, then engineering's and product's verdicts carry forward and qa's does not, `needs_reconsult` is exactly `["qa"]`, and the plan prints qa as owing a verdict on G2; a `--material` change carries none and lists every seat
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::OneRoundTests::test_only_a_seat_that_asked_is_re_consulted
- **AC3:** Given an open run whose recorded goal is G, when `sprint.py goal-review record --goal G2 --amend-from G --requested-by operator` runs, then it is accepted with no prior operator verdict, every seat's verdict carries forward and no seat's objection is discharged, the run state's `sprint_goal` reads G2 with G recorded as the wording it amended, and `close_goal_judgement` judges G2; an amendment whose `--amend-from` is not the open run's goal, or one recorded with no run open, leaves the run state unchanged; an amendment recorded after the run's goal verdict is refused naming that verdict, and the plan snapshot keeps the goal as planned
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::OpenRunGoalAmendTests::test_an_operator_amendment_moves_the_goal_the_close_judges
- **AC4:** Given the same open run and a G2 of 21 words, when the amendment is recorded, then it exits 2 naming the 20-word limit (`GOAL_WORD_LIMIT`), and neither the goal-review record nor the run state changes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::OpenRunGoalAmendTests::test_an_amended_goal_over_twenty_words_is_refused_and_nothing_is_written

## Notes

- Serves: Maya Okafor, End goal 3.
- AC1 must fail on: today's behaviour: only the requesting seat's verdict carried, which leaves two seats owing a second round
- AC2 must fail on: the field parsed and then ignored; a material change carrying verdicts
- AC3 must fail on: the run state left untouched (today only `sprint plan` writes `sprint_goal`, sprint.py:10247); the operator passed as a seat role, which collides with a project seat whose role is `operator`; the run goal moved to whatever `--amend-from` names; an amendment accepted after the goal verdict
- AC4 must fail on: the length check skipped on the amendment path (`goal_length_refusal` binds only the plan today); the round appended before the refusal
- D0390 and the drafting found that repeat rounds come from reference-sprint.md:320-325's documented practice, not from code.
- Overlap: id: BG1002; relation: related, stays its own: the goal-review brief also ignores changes made to an open run after `plan --write`; evidence: Title: 'goal-review brief ignores the plan's --serves and the batch changes made after plan --write'
- Overlap: id: CR0627; relation: same surface (`sprint.py goal-review`), different behaviour; with US1036 and US1037 under it; evidence: Title: 'goal-review brief is identical for every seat - give each seat its own lens and persona card'
- Risk: What drives repeat rounds today: `cmd_goal_review` carries forward only the requesting seat's verdict (sprint.py ~11314-11344), `goal_review_status` then lists every other seat in `needs_reconsult` (~3118), and reference-sprint.md:320-325 tells the reader 'the remaining seats are reported as needing a fresh verdict'. The plan never prints `needs_reconsult`, so the extra rounds come from the documented practice, and the doc changes with the code.
- Risk: Moving an open run's goal leaves other readers on the old wording: the plan snapshot (`extra["sprint_goal"]`, sprint.py ~10349), the plan-end content review (~10400) and a goal verdict already recorded with `sprint goal-verdict`. A recorded verdict on the old wording should be refused or cleared by the amendment; decide which at build.
- Risk: Three points, not the two first approved: the open-run goal amendment (AC3 and AC4) is the extra point.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | sdlc-studio | Created via `new` (deterministic) |
