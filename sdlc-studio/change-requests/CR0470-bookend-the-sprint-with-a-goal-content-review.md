# CR-0470: Bookend the sprint with a goal-content review: will this batch deliver the goal, and at close did it, given what was not delivered and what was raised

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (operator-raised, RUN-01KYKVZM close); agent; skill v5.0.0

## Summary

The goal review is a bookend and only one end exists, and that end asks the wrong question. Plan-time asks whether the goal is achievable rather than whether the chosen content delivers it; close-time asks nothing. The two questions are the same question asked before and after, and asking both is what makes a goal a commitment rather than a heading.

## Impact

Everyone planning or closing a sprint. The plan-time seat review that exists today asks whether the GOAL is achievable, whether it is one increment and what done would mean. It never asks the question that actually predicts the outcome: does THIS CONTENT - these specific units, at these sizes - deliver that goal. A batch can be sized, reviewed and approved while nobody has checked that the units chosen add up to the thing the sprint is for. At the other end there is no mirrored question at all, so a close reports units and points and never asks whether the goal was reached. RUN-01KYKVZM demonstrates both halves: its goal held three clauses, its 31 units were reviewed as achievable at plan, and at close one clause was only partially achieved because of a defect in the very unit meant to deliver it - a fact nobody was ever prompted to state, and which surfaced only because the operator asked directly.

## Acceptance Criteria

- [ ] At plan, once the batch is resolved, the reviewing seats are asked whether the chosen content will deliver the goal and a partially or no answer must name what is missing, proven by a test written red before the fix that refuses an unexplained partial
- [ ] At close, the seats are asked whether the delivered content achieved the goal, and the question is presented with the undelivered units and the defects raised against delivered units supplied rather than recalled, proven by a test written red before the fix
- [ ] Both answers are recorded on the run and the close shows them side by side, reporting a prediction miss where the plan predicted delivery and the close judges otherwise, proven by a test written red before the fix

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (operator-raised, RUN-01KYKVZM close) | Raised |
