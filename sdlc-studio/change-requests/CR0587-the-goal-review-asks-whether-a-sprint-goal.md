# CR-0587: the goal review asks whether a Sprint Goal is achievable, not whether it states value, so a shopping list passes

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/personas/seats, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** sdlc-studio/.local/goal-review.json (63 rounds, fields `achievable`, `done_means`, `one_increment`); RUN-01M2JA6J's approved goal text in .local/run-state.json; operator at the RUN-01M2JA6J close review, 2026-09-16.
> **Date:** 2026-09-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Each seat in the goal review answers exactly three fields - `achievable`, `done_means` and `one_increment` (sdlc-studio/.local/goal-review.json, 63 rounds recorded). All three are mechanical: can it be built, what would prove it, is it one increment. None asks whether the goal states VALUE - who is better off, and why the increment is worth a sprint - so a goal that is really a list of acceptance criteria passes with three YES votes. RUN-01M2JA6J's goal did: five rounds, three seats, and the approved text names sixteen unit ids, cites four decision records (D0193, D0194, D0196) and describes mechanisms ('reach Fixed on their own verifiers', 'held by the close's stop-ship step'). It is falsifiable and it was met - and it says nothing about why the work mattered. Read cold, it reports what was built. The operator raised it at the close: 'A sprint goal should be about value not a shopping list.' The same goal is quoted verbatim at the top of the end-of-run report (RFC0059), so the weakness is now in front of whoever signs.

## Impact

The operator, and the next planner. A goal that enumerates units cannot arbitrate scope mid-run - every unit is in the goal by name, so nothing can be dropped without the goal failing, and the goal stops being the thing the batch serves. It also makes the run unreadable to anyone outside it.

## Acceptance Criteria

- [ ] Each seat's goal-review record carries a VALUE answer naming who is better off and how they would notice, and a goal with no value answer from any seat is refused
- [ ] A goal whose text carries a unit id or a decision-record citation is refused, naming each one and pointing at the acceptance criteria as their home
- [ ] The refusal is proven on RUN-01M2JA6J's own approved goal as a fixture - it must be refused by both rules - beside a value-shaped rewrite of the same goal, which must pass
- [ ] reference-sprint.md states the rule in the goal section, and the seat briefs ask the value question in the seat's own words

## Recommendation

Add a VALUE field to the goal review - one per seat, answering who is better off and how they would notice - and refuse a goal whose text carries unit ids or decision-record citations, naming them: those belong in the acceptance criteria the goal is judged by, never in the goal. Keep the three existing fields; the failure is an absent question, not a wrong one. RUN-01M2JA6J's goal rewritten under the rule reads: 'The project's status can be trusted by whoever reads it next: a unit at Done is finished, a run that ended left no question behind it, and a red corpus lane on main means a real defect rather than a broken runner' - same three limbs, still falsifiable, no ids.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Raised |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - goal review asks value: US0868 / D0253 one-sentence value goal with advisory seat read |
