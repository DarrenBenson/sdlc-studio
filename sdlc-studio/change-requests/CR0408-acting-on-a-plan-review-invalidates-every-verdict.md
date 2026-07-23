# CR-0408: Acting on a plan review invalidates every verdict including the one that proposed the change, so improving a goal costs a full re-consult

> **Status:** In Progress
> **Decomposed-into:** EP0152
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found on the first live Sprint Goal review. The engineering seat rejected the goal and supplied a reframed sentence. Adopting that sentence - the single most useful thing the review produced - invalidated all three recorded verdicts, INCLUDING engineering's own, because a verdict is pinned to the goal string it judged. Answering the review therefore required consulting all three seats again.

The pinning is right and must stay: it is the wsjf-inputs lesson, that a judgement from a closed era must not silently discharge a live gate. The problem is that the pin has no notion of an AMENDMENT, so the system cannot tell these two cases apart: a goal quietly swapped for a different one after review, which must invalidate everything, and a goal edited to do exactly what a seat asked, where that seat's position is known and the other seats' may or may not still hold.

The incentive this creates is the damaging part. The cheapest path through the gate is to leave the goal exactly as first written, because any improvement costs another full round. A review whose findings are expensive to act on will be acted on less. That is the opposite of what the ceremony is for, and it is the same economics CR0404 identifies in the sprint review one rung later.

Measured cost here: three subagent consults to change one sentence in the direction a seat had itself requested.

## Impact

Every project that runs the goal review, and it bites hardest on the reviews that go well - a review that finds nothing costs one round, a review that finds something real costs two. It also silently discourages the operator amendment path, since an operator refining the wording after reading the verdicts pays the same full price as someone substituting a different goal.

## Acceptance Criteria

- [ ] A goal can be AMENDED against a recorded review, carrying forward the verdicts of seats whose stated position the amendment satisfies, and requiring only the seats it does not.
- [ ] An amendment records the previous wording and which seat asked for the change, so the trail shows the goal was improved rather than replaced.
- [ ] A change that is NOT an amendment - a materially different goal - still invalidates every verdict, exactly as today. Where the distinction cannot be made mechanically it is the operator's declaration, recorded, not the tool's guess.
- [ ] The staleness protection is unchanged: a verdict from a previous sprint can never discharge a current goal, amendment or not.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
