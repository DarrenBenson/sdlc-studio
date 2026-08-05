# CR-0532: The reviewer of record is an AI seat, and the human gets a summary to lead from - human in the LEAD, not human in the loop

> **Status:** In Progress
> **Decomposed-into:** EP0209
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/personas/seats/, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/help/critic.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Today the two-role gate requires a reviewer of record the authoring session does not control, and in practice that means a person typing `critic.py signoff`. The independence rule is right; the assumption that independence requires a HUMAN is the part that does not follow, and it is what makes a run stop dead waiting for someone to be awake.

RUN-01KZ79C1 is the evidence in both directions. The adversarial half worked superbly WITHOUT a human: two fresh-context amigo seats, briefed by the shipped tool, independently found 11 blocking defects that every automated gate had passed - including five criteria pinned by verifiers that could not fail. They converged on identical unit-level splits without contact. That is a stronger independence signal than one tired person reading a diff at the end of a long day.

The sign-off half then blocked for hours on a human keystroke, over work the AI seats had already judged in more depth than any human review of ten units would.

The proposal: a named amigo seat - one that did not author the diff and did not run the adversarial pass - becomes the REVIEWER OF RECORD. It signs, and the act generates an operator SUMMARY: what shipped, what was rejected and why, what is carried and where it is filed, what it cost, and the one or two judgements the operator should overturn if they disagree. The human leads by reading a decision-grade summary and reversing what they choose to, rather than by being the gate every unit queues behind.

This is the cockpit model applied to the review gate: instruments report, the human flies. It is not a relaxation of the independence rule - it is the recognition that independence is about SEPARATE CONTEXT AND SEPARATE INCENTIVES, which a fresh seat has and a rubber-stamping human does not.

## Why now - the operator's framing

**Human in the loop is too slow for true AI speed. Human in the lead is the best approach.**

That is the whole argument, and this run measured it. The adversarial pass - two seats, 11
blocking findings, identical splits reached without contact - took minutes of wall-clock and no
human attention at all. The sign-off then held the run for hours over work those seats had
already judged more thoroughly than any human review of ten units would.

The asymmetry is structural, not incidental. Review depth scales with AI capacity; a human
gate scales with one person's availability. Putting the slower of the two in series with every
unit means throughput is set by the human, and the human's contribution at that point is
weakest - they arrive last, with less context than the seats that just did the work, which is
precisely the condition that produces rubber-stamping. A gate that pressures its holder toward
approval is worse than no gate, because it manufactures a record of judgement that was not
exercised.

Human in the lead inverts the series. The seats judge, at their speed. The operator reads a
decision-grade summary and reverses what they disagree with, at theirs. Nobody waits on
anybody, and the human's attention lands where it is actually differentiated: on what the
product should be, not on whether a test discriminates.

## Impact

Who: every operator running sprints, and every consuming project where the sign-off is the reason a run sits open overnight. What breaks today: a run cannot close without a human act, so throughput is bounded by human availability rather than by the work - and the human, arriving at the end, has less context than the seats that just reviewed it, which pushes toward rubber-stamping. That is the failure mode the two-role gate exists to prevent, reached from the other side.

What this buys: an autonomous run can close on its own evidence with a named accountable seat, and the operator reads a summary and intervenes where they disagree. It is also what makes rolling `--cycles` runs and the charter queue genuinely autonomous - both exist today and both stop at the sign-off.

## Acceptance Criteria

- [ ] Three distinct contexts are enforced, not requested: the signing seat is neither the author nor the seat that ran the adversarial pass, and the existing self-approval guard refuses a sign-off that collapses any two of them.
- [ ] A sign-off records WHO judged and in what capacity, so no reader can mistake an AI seat's signature for a human's - the record says `seat` and names it, and a consuming project reading the ledger can filter on it.
- [ ] The operator summary is DERIVED from the record - what shipped, what was rejected and why, what is carried and where it is filed, what it cost - and is not prose the signing seat composes about its own decision.
- [ ] The summary names the judgements the operator is most likely to want to overturn, so leading is a bounded act rather than re-reading the whole batch.
- [ ] A reversal path exists and is exercised by a test: the operator rejects a seat's sign-off, and the affected units return from Done to Review with the reversal recorded against the seat that signed.
- [ ] Which work a seat may sign is bounded by a declared policy rather than by judgement at the moment of signing, and the shipped default keeps product-shaped rulings - a criterion that cannot be made decidable, whether a feature may ship absent - with the human.
- [ ] A run that closes on a seat's sign-off is indistinguishable in the close chain from one closed on a human's, EXCEPT in the record - so no second code path exists to drift.

## Recommendation

Option 2, tiered by blast radius, because it composes with CR0510 rather than duplicating it - and because this run showed exactly where the line sits. The seats' judgement on ten units was better than a human's would have been. But the two findings that most needed an operator - BG0525 (a criterion that is not mechanically decidable, so it needs restating rather than implementing) and the ruling on whether a config key that does nothing may ship - are product judgements, not review judgements. Tier on that distinction: a seat signs correctness, a human rules on what the product should be.

HARD CONSTRAINTS, whichever option is taken. The signing seat must be neither the author nor the adversarial reviewer - three distinct contexts, and the existing self-approval guard must extend to cover it. The summary is generated from the RECORD, never written by the signing seat as prose, or it becomes a seat marking its own homework. And the record must state plainly that the sign-off was an AI seat's, so no reader can mistake it for a human's - the point is transparency about who judged, not a simulation of a human having done it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Raised |
