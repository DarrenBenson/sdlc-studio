# CR-0402: Gate a repair on a reviewed PLAN, so a round's findings are answered deliberately rather than fixed at speed

> **Status:** Superseded
> **Parent:** RFC0053
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py,.claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/reference-review.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator decision at the RUN-01KY3MFX close, filed by Claude Opus 4.8

## Summary

Operator decision at the RUN-01KY3MFX close, taking RFC0053 option B. The repair is the only step in the delivery loop with no review before execution: a story's implementation plan is gated by `plan_review.py`, the code is reviewed after it is written, and the repair between them has neither. It is also where this sprint's defects were manufactured - every round from 3 to 10 found at least one defect created by the previous round's repair, and in each case the flaw was in the APPROACH and would have been visible in a written plan. Rounds 4, 5 and 6 each planned to enumerate a matcher's literal spellings when the answer was to probe its predicate; a reviewer reading the word enumerate would have asked why not derive, and three rounds would not have happened. Round 9 found a false count written into a paragraph while correcting a false count in the same paragraph. Round 8 found a plan to remove all superlatives that removed one and whose retraction added a new ranking. The author's own summary of the failure, and the reason this is worth building: the repairs were vibe-coded - read the finding, start editing - rather than thought about, written down, attacked, and only then executed with the explicit goal of passing the next round.

## Impact

Every closing review in every consuming project, and the cost is measurable rather than theoretical. RUN-01KY3MFX ran ten adversarial rounds at roughly 100,000 to 200,000 tokens each. The code converged after seven; the prose never did, because each repair generated the next round's findings. A repair plan reviewed before execution attacks that loop at its source, and it is cheap next to the round it prevents.

## Acceptance Criteria

- [ ] A REJECT verdict produces a written repair plan naming, per finding: what will change, why that approach and not an alternative, and what the change might break or leave unguarded.
- [ ] The plan is put to an independent adversarial pass BEFORE any code is written, briefed with the specific questions this sprint kept failing - does the fix introduce the class it repairs; is it a restatement of a rule that lives in code elsewhere, and could it be DERIVED instead; what did the previous attempt believe that turned out to be false.
- [ ] The plan review is PINNED to the findings it answers, so a later finding invalidates it, following the precedent `plan_review.py` already sets by pinning a story's plan to its ACs.
- [ ] The repair's own commit records which plan it executed, so a later reader can tell a planned repair from an unplanned one.
- [ ] The gate is opt-in per project and OFF by default, so an existing project's close does not change until it asks for this.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | Darren Benson | Raised |
