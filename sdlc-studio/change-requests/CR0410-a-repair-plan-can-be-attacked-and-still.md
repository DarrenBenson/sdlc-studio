# CR-0410: A repair plan can be attacked and still repeat the previous approach, so a class that has failed N rounds must force a design decision rather than a better instance

> **Status:** In Progress
> **Decomposed-into:** EP0106
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py,.claude/skills/sdlc-studio/reference-review.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator observation after RUN-01KY5EJX, filed by Claude Opus 4.8

## Summary

Measured on RUN-01KY5EJX, which is the run that groomed EP0106 and dogfooded its discipline by hand. One repair round was planned and independently attacked; three were not. All four seeded the next round's defect, INCLUDING the planned one.

The planned round is the informative case. The plan was refuted outright and the attacker supplied a better approach - real value, and it found two escapes the code review had missed. But the approach it supplied carried a false premise about the tool (`discard directory entries unless -r`, which is true of grep and false of this DSL, whose runner always recurses). Author and reviewer held the same wrong belief, so the review could not catch it, and round 2's MAJOR was created by the reviewed plan.

What eventually broke the chain was not a better plan. Five successive versions had tried to ENUMERATE what a grep verifier reads, each defeated by a case it had not considered, and round 4 abandoned the approach class instead - inverting the burden so that anything unproven refuses. That is a design change, and nothing in the loop asked for it. Each round had asked only 'what is wrong with this repair', never 'should we still be repairing within this design'.

EP0106's five stories cover the plan, its independent review, the pinning, the commit provenance and the opt-in. None of them asks that question. A reviewer briefed with the four questions in US0312 would have interrogated the fix and not the family it belongs to.

The threshold matters and should not be invented. Two consecutive failures of one approach can be bad luck; five is a signal about the design. Whatever number is chosen, the point is that it is REACHED and then FORCES a recorded decision, rather than leaving it to whoever happens to notice the pattern.

## Impact

Every project using the repair-plan gate once EP0106 ships, and the cost is measurable here: rounds 2, 3 and 4 of RUN-01KY5EJX were all repairs within a design that had already failed, at roughly 100,000 to 200,000 tokens per round plus the repair. A rule that forced the design question after round 2 would have reached round 4's answer two rounds earlier. It also protects against the specific failure the planned round demonstrated, where an independent reviewer improves the instance while sharing the author's premise.

## Acceptance Criteria

- [ ] When a repair answers a finding in the same class as a previous round's, the plan is required to state whether the DESIGN is being retained or changed, and why - a plan that only describes a better instance is refused once the threshold is reached.
- [ ] The threshold is configurable and its default is stated with the evidence it rests on, rather than being asserted as a round count somebody chose.
- [ ] The reviewer's brief carries the question explicitly: not only 'is this fix correct' but 'has this approach failed often enough that the approach is the defect'.
- [ ] A recorded decision to RETAIN the design is a first-class outcome, not a failure to change it - the point is that the question was asked and answered on the record.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | Darren Benson | Raised |
