# CR-0469: A sprint-goal-achieved verdict judged by a stakeholder panel, which decides whether an open defect can be left or must be addressed before close

> **Status:** In Progress
> **Decomposed-into:** EP0185
> **Priority:** High
> **Type:** Feature
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (operator-raised, RUN-01KYKVZM close); agent; skill v5.0.0

## Summary

The close reports units, points and drift and never reports a verdict on the Sprint Goal itself. Two decisions hang off a verdict that does not exist: whether the sprint achieved what it was for, and whether each open defect is leavable. Both are currently taken informally by the author, who is the least independent party available and the one whose work is being judged.

## Impact

Every actor in the loop. Today a sprint close answers 'how many units reached Done' and never answers 'was the goal achieved', so the close decision - can this defect be left until next sprint, or does it have to be fixed now - is taken by whoever is holding the keyboard, using a severity they assigned themselves. Observed on RUN-01KYKVZM: ten defects were filed against units in the batch, the author graded them by hand with no panel and no rubric, and two of those hand-gradings were wrong in both directions when actually tested - one filed High was in fact harmless because the index it reported missing is created on demand, and one filed Medium turned out to let a bug reach a terminal status with zero acceptance criteria on the tool's own default path. The count of units said 31 of 31 while a clause of the goal was not achieved at all. Without this, a sprint can close green on the arithmetic while the thing it was for did not happen, and a release can go out carrying a defect nobody graded against user impact.

## Acceptance Criteria

- [ ] A Sprint Goal is recorded as clauses at plan time and the close reports a verdict per clause, so a goal achieved in part is expressible, proven by a test written red before the fix over a three-clause goal landing differently on each
- [ ] The per-clause verdict is returned by a panel of seats that never includes the author, and a panel including the author is refused rather than warned, proven by a test written red before the fix
- [ ] An open defect is judged against the goal clauses, a defect falsifying a clause blocks the close, and a defect that does not is recorded as leavable with its priority and the clause reasoning, proven by a test written red before the fix
- [ ] A run whose units all reached a terminal status but whose goal was not achieved reports that in the close and in the retro rather than reporting only the unit count, proven by a test written red before the fix

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (operator-raised, RUN-01KYKVZM close) | Raised |
