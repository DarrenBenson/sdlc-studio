# CR-0398: There is no batch-size heuristic, and the measured fixed cost makes the obvious advice backwards

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md,.claude/skills/sdlc-studio/help/sprint.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

CR0391 measured a fixed cost of roughly 3,884,000 tokens per sprint against a marginal of roughly 13,105 per point, from the only two sprints measured whole. If that holds, keeping batches small is expensive here: 18 points cost at least 228,884 per point and 100 points at least 51,945, a 4.4x difference driven almost entirely by amortising the ceremony. The same sprint gives the counter-evidence: 100 points produced 11 MAJORs in one round, bulk repairs masked defects beside them three times, and six rounds ran without converging to APPROVE. A small batch is expensive per point and cheap to review; a large one is the reverse. Nothing in the guidance names this trade-off, so the decision with the widest consequences at plan time rests on instinct with no stated model.

## Impact

Every plan. Batch size drives both token cost and the number of review rounds needed to converge, and the two pull in opposite directions.

## Acceptance Criteria

- [ ] The sprint guidance states the trade-off: fixed cost falls per point as the batch grows, review convergence cost rises with it.
- [ ] It is grounded in this project's own measured rows and names how many sprints it rests on.
- [ ] It prescribes NO number: with two measured sprints there is no defensible optimum, and inventing one repeats the mistake BG0254 was filed about.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
