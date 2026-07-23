# RFC-0052: The closing review converges on code and never on prose, so a sprint can be unable to clear its own critiqued gate

> **Status:** Superseded
> **Triage:** DELIVERED - carry-forward (recommendation D) shipped as CR0404/EP0113, claim-inventory (C) as CR0393/EP0109, both RUN-01KY5Y3W; residual structural count-check is a minor follow-up if wanted
> **Decomposed-into:** CR0404
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py,.claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/reference-review.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Measured over seven adversarial rounds on RUN-01KY3MFX. The CODE converged cleanly: 11, 6, 3, 1, 1 and 2 MAJORs, and round 7 found no logic defect at all, stating that both production-code repairs under review were correct and it would sign them off on their own. The PROSE never converged. From round 3 onward every single round's surviving findings were claims about code rather than code - a Resolution saying mutation-proven when the mutants never reached the lane, an enumeration whose count was wrong at three, four, five, six and seven with two of the items positively DENYING the case the next round found, a CLI sentence wrong five times running, and an assertion pinning a word rather than a claim. Each repair was written by an author who had just read the previous failure. The mechanical consequence is a genuine loop: `conformance.sprint_covers_independently` accepts a sprint-level review as evidence ONLY when the verdict is APPROVE, so seven REJECTs leave all 33 units reading `missing critiqued`, every commit blocked, and the sprint unable to close its own paperwork even though the operator has signed off and the code is sound. The loop is not a bug in the gate - the gate is telling the truth. It is that the deliverable includes prose, prose has no executable oracle, and an adversary reading prose will essentially always find something, so the round count is bounded by patience rather than by convergence.

## Design Options

- **A: accept that prose findings are advisory - a round returns APPROVE when no LOGIC defect survives, and prose findings are filed as follow-ups rather than blocking the verdict. Honest about what the gate can actually decide, and stops the loop today. Risk: prose is where this project's real defects have lived for nine rounds, so downgrading it wholesale discards the review's best output.**
- **B: split the verdict - a round returns a code verdict and a prose verdict separately, and only the code verdict feeds `critiqued`. The prose verdict accumulates as filed findings with no gate power. Keeps the signal, removes the block.**
- **C: give prose an oracle. Most of the seven rounds' prose findings were of two mechanical kinds - a claim contradicted by the code it describes, and an enumeration whose header count disagrees with its own body. Both are checkable. A claim-inventory check (CR0393) plus a structural check that a stated count matches the items enumerated would have caught the majority automatically and cheaply, before any reviewer read them.**
- **D: bound the rounds by evidence rather than by ceiling - stop when a round finds nothing that changes BEHAVIOUR, recording the outstanding prose findings on the close. Explicit about what is being accepted.**

## Recommendation

B plus C, with D as the stopping rule. C is the real fix and is cheap: a header asserting SEVEN items over a list of six is a structural error a linter finds instantly, and it went undetected through two rounds of humans and agents reading carefully. Most of the enumeration failures on this sprint are of exactly that shape. B unblocks the gate without discarding the signal, which A does. D replaces a patience-bounded loop with an evidence-bounded one, and its stopping condition is honest in a way 'the ceiling was spent' is not. Note what should NOT be adopted: raising `review.max_rounds`. Seven rounds did not converge on prose and an eighth would not either; the answer is to stop asking a human-judgement question of a gate that can only accept APPROVE.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between: A: accept that prose findings are advisory - a round returns APPROVE when no LOGIC defect survives, and prose findings are filed as follow-ups rather than blocking the verdict. Honest about what the gate can actually decide, and stops the loop today. Risk: prose is where this project's real defects have lived for nine rounds, so downgrading it wholesale discards the review's best output., B: split the verdict - a round returns a code verdict and a prose verdict separately, and only the code verdict feeds `critiqued`. The prose verdict accumulates as filed findings with no gate power. Keeps the signal, removes the block., C: give prose an oracle. Most of the seven rounds' prose findings were of two mechanical kinds - a claim contradicted by the code it describes, and an enumeration whose header count disagrees with its own body. Both are checkable. A claim-inventory check (CR0393) plus a structural check that a stated count matches the items enumerated would have caught the majority automatically and cheaply, before any reviewer read them. or D: bound the rounds by evidence rather than by ceiling - stop when a round finds nothing that changes BEHAVIOUR, recording the outstanding prose findings on the close. Explicit about what is being accepted. | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
