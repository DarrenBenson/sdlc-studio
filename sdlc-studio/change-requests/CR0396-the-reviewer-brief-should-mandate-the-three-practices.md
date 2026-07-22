# CR-0396: The reviewer brief should mandate the three practices that produced this sprint's best findings, rather than leaving them to whoever writes the brief

> **Status:** In Progress
> **Decomposed-into:** EP0108
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/reference-review.md,.claude/skills/sdlc-studio/scripts/critic.py
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

RUN-01KY3MFX ran five adversarial rounds and the three highest-value practices were all improvised by the author mid-sprint rather than drawn from any template. (1) PER-ITEM REPAIR VERDICTS: from round 2 the brief required the reviewer to rule on each previous finding as CLOSED, OVER-CLAIMED or MOVED. That produced the single most useful artefact of the whole sprint - 5 closed, 3 over-claimed, 3 moved - and a general 'review the repair' brief would have blurred all three categories into one impression. (2) MUTATION-TESTING THE AUTHOR'S TESTS, not only the code: round 5's best finding was that a test's shape list had been selected from exactly the families where two implementations agree by construction, while its comment claimed they could not diverge. No amount of reading the code finds that. (3) ISOLATION RE-TESTING OF A SURVIVING MUTANT: a mutant survived three separate times this sprint because a SIBLING guard masked the branch, and each time the truth only appeared when the branch was exercised alone. A reviewer who treats a survivor as evidence about the test rather than about the harness draws the wrong conclusion.

## Impact

Every closing review, and every consuming project adopting the review model. Today these practices depend on the author remembering to ask for them, which means the review is only as good as the brief the author happened to write - and the author is the party the review exists to check.

## Acceptance Criteria

- [ ] The shipped reviewer brief carries all three as standing instructions, with the reason each exists stated beside it.
- [ ] A repair review is briefed with the previous round's findings enumerated, and returns a per-item verdict for each.
- [ ] The brief states that a surviving mutant is re-tested in isolation before any conclusion is drawn from it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
