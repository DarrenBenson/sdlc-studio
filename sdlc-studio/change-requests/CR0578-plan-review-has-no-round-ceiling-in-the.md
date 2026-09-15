# CR-0578: Plan review has no round ceiling in the tooling; D0204's three-round cap is a ruling nothing enforces

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** D0204, recorded 2026-09-15 on the operator's ruling in RUN-01M2JA6J; round counts from sdlc-studio/reviews/plan-review-verdicts.md (BG0667 6, BG0671 5, US0626 4).
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

D0204 caps plan review at three independent QA rounds per unit: after the third REJECT the author repairs the blocking items, records a complete repair, and the entry gate clears on it. Today that lives only in the decision log. Nothing counts plan-review rounds, nothing tells the author the cap is reached, and nothing stops a fourth brief being generated, so the cap holds only while someone remembers it. Delivery rounds have the same shape of rule (D0146) and the same gap. RUN-01M2JA6J ran units to six rounds before the ruling.

## Impact

Operators and authoring agents running plan review: without a gate, review rounds grow until someone notices the cost, and a ruling that is only prose is the class of rule this repository keeps finding unfollowed (LL0027).

## Acceptance Criteria

- [ ] critic.py brief --phase plan-review refuses a round past `review.plan_review_round_cap` for a unit, naming the count, the cap and the repair route, beside a unit under the cap that briefs normally
- [ ] The test-plan entry gate's refusal for a unit at the cap names the repair route rather than asking for another review
- [ ] A complete plan-review repair past the cap clears the entry gate, and one leaving any finding without a fixed, carried or filed disposition does not
- [ ] `review.plan_review_round_cap` is declared in the shipped defaults with its consumer named, and an unset key reads as 3

## Recommendation

Count a unit's plan-review rounds from the verdict ledger (distinct REJECT briefs of kind test-plan). Add `review.plan_review_round_cap` (default 3; a distinct key - `review.max_rounds` is deliberately absent). At the cap: critic.py brief --phase plan-review refuses a further round and names the author's route (repair every finding, then the gate clears on the complete repair); the gate's refusal message names the same route; a complete repair past the cap must dispose of every finding as fixed, carried or filed, so nothing raised is dropped. Consider the same count for delivery rounds under D0146.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
