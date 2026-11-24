# BG1608: goal-review brief and a first-round record accept a goal over the 20-word limit that sprint plan and an amendment refuse

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/BG1608.md
> **Evidence:** run eighteen's planning, 2026-11-19: orchestrator; goal-review rounds 12 and 13 recorded at 37 and 60 words, the amendment refused at 62
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T08:55:29Z

## Summary

`goal_length_refusal` binds `sprint plan` and a `goal-review record --amend-from`, but not `goal-review brief` or a first-round `goal-review record`. Run eighteen's goal was briefed at 37 words and recorded over two rounds of three seats (the second at 60 words) with no warning. Only the third round, recorded with `--amend-from`, was refused at 62 words, so the seats had judged wording the plan could never take, and a fourth round was needed to confirm a 20-word version.

Reproduced at cecc9dfe7 (2026-11-24) with a 30-word goal on `test_goal_review_one_round.py`'s `base` fixture: `goal-review brief --goal <it> --seat qa` exits 0, a first-round `goal-review record --goal <it> --seat qa|yes|done|yes` exits 0 and writes the round, while `goal-review record --amend-from` and `sprint plan --sprint-goal` each exit 2 with `the Sprint Goal is 30 words and the limit is 20`. In `cmd_goal_review` the only `goal_length_refusal` call sits inside `if amend_from:`, and the brief branch calls none. reference-sprint.md says only that an amended goal over 20 words is refused.

## Steps to Reproduce

Run `sprint.py goal-review brief --goal '<a 30-word goal>' --brief-worklist <file>`, then `goal-review record --goal '<the same goal>' --seat ...`: both succeed. Then `goal-review record --goal '<a 30-word amendment>' --amend-from '<the first goal>' --seat ...`: it is refused for length.

## Proposed Fix

Apply `goal_length_refusal` in `goal-review brief` (when a goal is given) and in every `goal-review record`, on the goal as resolved from `--goal` or `--fields-file`, before anything is printed or written, so the length is met before any seat reads the goal. Say so in reference-sprint.md.

## Acceptance Criteria

- [ ] **AC1** Given a project ready to brief, when `goal-review brief --goal <21 words> --seat qa` runs, then it exits 2 with the goal-length refusal and prints no brief on stdout; the same command with a 20-word goal (the control) exits 0 with the brief. Fails on: rc 0 with a brief for a goal the plan will refuse.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::GoalLengthAtReviewTests::test_the_brief_refuses_a_goal_over_twenty_words
- [ ] **AC2** Given no goal-review round recorded, when a first-round `goal-review record` names a 21-word goal, by `--goal` and again by a `--fields-file` goal, then each exits 2 with the goal-length refusal and goal-review.json is not written; a 20-word goal (the control) is recorded. Fails on: rc 0 with the round written, so the seats judge wording the plan can never take.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::GoalLengthAtReviewTests::test_a_first_round_record_refuses_a_goal_over_twenty_words

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe7; two executable criteria with the 20-word boundary as control; Affects drops test_sprint.py and adds reference-sprint.md |
