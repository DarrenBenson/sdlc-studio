# BG1608: goal-review brief and a first-round record accept a goal over the 20-word limit that sprint plan and an amendment refuse

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py, changelog.d/BG1608.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** run eighteen's planning, 2026-11-19: orchestrator; goal-review rounds 12 and 13 recorded at 37 and 60 words, the amendment refused at 62
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T08:55:29Z

## Summary

`goal_length_refusal` binds `sprint plan` and a `goal-review record --amend-from`, but not `goal-review brief` or a first-round `goal-review record`. Run eighteen's goal was briefed at 37 words and recorded over two rounds of three seats (the second at 60 words) with no warning. Only the third round, recorded with `--amend-from`, was refused at 62 words, so the seats had judged wording the plan could never take, and a fourth round was needed to confirm a 20-word version.

## Steps to Reproduce

Run `sprint.py goal-review brief --goal '<a 30-word goal>' --brief-worklist <file>`, then `goal-review record --goal '<the same goal>' --seat ...`: both succeed. Then `goal-review record --goal '<a 30-word amendment>' --amend-from '<the first goal>' --seat ...`: it is refused for length.

## Proposed Fix

Apply `goal_length_refusal` in `goal-review brief` and in every `goal-review record`, so the length is met before any seat reads the goal.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `goal_length_refusal` binds `sprint plan` and a `goal-review record --amend-from`, but not `goal-review brief` or a first-round `goal-review record`.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run `sprint.py goal-review brief --goal '<a 30-word goal>' --brief-worklist <file>`, then `goal-review record --goal '<the same goal>' --seat ...`: both...
- [ ] **AC3** The proposed fix lands, pinned by a test: Apply `goal_length_refusal` in `goal-review brief` and in every `goal-review record`, so the length is met before any seat reads the goal.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
