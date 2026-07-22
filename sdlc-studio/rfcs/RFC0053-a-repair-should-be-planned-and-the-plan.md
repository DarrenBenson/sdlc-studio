# RFC-0053: A repair should be planned and the PLAN adversarially reviewed, because the repair is the only step in the loop with no review before execution

> **Status:** Accepted
> **Decomposed-into:** CR0402, EP0106
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py,.claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/reference-review.md,.claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator proposal at the RUN-01KY3MFX close, filed by Claude Opus 4.8

## Summary

Operator proposal, and RUN-01KY3MFX is the evidence for it. Ten adversarial rounds ran. Every round from 3 onward found at least one defect that the PREVIOUS round's repair had created, and in each case the flaw was visible in the APPROACH rather than in the code: round 9 found a false over-fire count written into the same paragraph while correcting a false escape count; round 8 found a plan to 'remove all superlatives' that removed one and whose retraction added a new ranking claim; rounds 4, 5 and 6 each enumerated a matcher's literal spellings when the answer was to probe the matcher's own predicate, which is what finally worked. A reviewer given the sentence 'I will enumerate the spellings' would have asked why not derive, and three rounds would not have happened. The structural observation: this loop reviews the PLAN before a story is built (`plan_review.py` exists and gates exactly that, pinned to the story's ACs so a later edit invalidates the verdict), and it reviews the CODE after it is written. The repair sits between them with neither. It is also the most defect-dense work in the sprint - repairs are written fast, under the belief that the previous failure is now understood, by the author the review exists to check. Three separate times on this sprint a repair MASKED the defect beside it. The proposal is to close that gap with machinery that already exists: a review's findings become a written repair plan - what will change, why that approach rather than another, and what the fix might break - and the plan is put to an adversarial pass before any code is written, with the explicit goal that the resulting repair passes the next round.

## Design Options

- **A: reuse `plan_review.py` as-is. A repair plan is recorded and gated like a story's implementation plan, pinned to the findings it answers so a later finding invalidates it. Smallest change, uses a surface already built and tested.**
- **B: a distinct repair-plan pass with its own prompts, because the questions differ from a build plan's. A build plan is asked whether it delivers the ACs; a repair plan should be asked whether the fix introduces the class it repairs, whether it is a restatement of a rule that lives elsewhere, and what the previous attempt got wrong.**
- **C: fold it into the reviewer's own output - the round that REJECTS also proposes the repair approach, and a second instance attacks that proposal. Cheapest in wall-clock since the reviewer already holds the context, but it makes the finder the designer, which is the coupling the two-role model exists to avoid.**
- **D: do nothing and rely on the round loop to converge. This is the status quo and RUN-01KY3MFX measured it: ten rounds, no convergence on prose, and a conformance gate that cannot clear because it accepts only an APPROVE.**

## Recommendation

B, delivered by extending `plan_review.py` rather than building a second surface. The questions genuinely differ and they are the ones this sprint kept failing: does this fix introduce the class it repairs; is it a restatement of a rule that lives in code elsewhere, and could it be DERIVED instead; what did the previous attempt believe that turned out to be false; and what does the fix leave unguarded. Three of those four would have caught a real defect on this sprint. Reject C: the reviewer that finds a defect is the worst-placed party to design its repair, and the whole model rests on that separation. Reject D on measured grounds rather than principle - it was tried here for ten rounds and the code converged while the prose did not, which is RFC0052's finding. Sequencing note: this RFC and RFC0052 are two halves of one problem. RFC0052 asks what a verdict should GATE when prose never converges; this asks how to stop generating the prose defects in the first place. Building this one first would make RFC0052's question less urgent, because most of what failed to converge was repair-authored prose.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | RESOLVED - option B: a distinct repair-plan pass with its own prompts, extending `plan_review.py` rather than building a second surface. The questions a repair plan must answer differ from a build plan's, and they are the ones RUN-01KY3MFX kept failing. C is rejected because it makes the reviewer that FOUND a defect the designer of its repair, which is the coupling the two-role model exists to prevent. D is rejected on measured grounds: it was the status quo for ten rounds and the prose never converged. Operator decision at the RUN-01KY3MFX close. | Resolved |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | Darren Benson | Filed |
