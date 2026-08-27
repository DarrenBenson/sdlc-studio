# CR-0507: closing a sprint asks twenty questions when it should ask two, and the ceremony now costs more than the work it certifies

> **Status:** In Progress
> **Decomposed-into:** EP0224
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-doctrine.md
> **Date:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator), from the RUN-01KYPZ1G close; human; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

A sprint close should answer two questions: is the Sprint Goal met, and is any stop-ship defect open? Everything else is bookkeeping that should be DERIVED and reported, not gated. What ships instead is a nine-step chain (review-coverage, retro-validate, retro-extract, retro-accuracy, lessons-summary, gate, handoff, reconcile, review-anchor), eleven flags on one command, and a preflight that returned twenty unmet prerequisites on a run whose work was finished and green. Measured on RUN-01KYPZ1G: the delivery was done and the full suite was green, and the close then consumed the larger part of a session across seven independent reviewers, three repair rounds, a hand-corrected review anchor, a coverage predicate with three lanes, per-unit sign-off items, conformance waivers, and a bounded-exit path that then refused. The previous run recorded the same shape in its own numbers: 5h to deliver, 6h35m to close, of which only about 18% was gate and suite time. A close that costs more than the sprint is not a quality gate; it is the reason a future close gets skipped.

## Impact

Who: the operator, who wants to know whether the sprint is closeable and instead conducts an interview; and every consuming project, which inherits this ceremony as the shipped definition of done. What breaks: three things, all worse than slowness. First, the two questions that matter are BURIED - the goal verdict and the stop-ship judgement are two lines among twenty, so the signal is indistinguishable from the bookkeeping. Second, a ceremony this large gets bypassed rather than followed, which this repo has now attested three times over (the seat ceremony, the waiver shrink rule, the review standing practices), and a bypassed gate protects nothing. Third, it inverts the incentive on honesty: every additional gate is another thing an author is tempted to satisfy rather than answer, and the close's own instruments were found this run to be reporting figures they could not compute.

## Acceptance Criteria

- [ ] The close GATES on two questions and no others: is the Sprint Goal met (achieved / partial / missed, with its rationale), and is any OPEN defect a stop-ship. Every other current step becomes a derived report printed beside the verdict - stated, never blocking. A step that cannot answer its question reports UNKNOWN rather than refusing, on the same principle the repo already applies to a dead-flag destination it cannot judge.
- [ ] The stop-ship question is answered per defect and the ruling is RECORDED with who made it, since it is a judgement rather than a measurement. `judge_defects_against_goal` already exists and already answers it; it is currently one input among many rather than one of the two gates.
- [ ] A sprint closes with open defects. That is the normal case, not an exception needing a waiver: a close records what is carried and what it was ruled, and only a stop-ship holds it. The waiver machinery currently absorbing this (D0074, D0077-D0087) exists because closing over known issues has no first-class representation, and a waiver misdescribes what happened - nothing was bypassed, a judgement was made.
- [ ] A review verdict is judged on the REVISION it was given for. A REJECT that has been repaired is retired by a recorded re-review, and a stale verdict does not gate a close forever - this is CR0506, and it is a precondition rather than a sibling: without it the first gate cannot be satisfied by the ordinary reject-fix-rereview loop every human team uses.
- [ ] The close's own cost is measured and reported against the delivery's, because the failure this CR names is invisible until those two numbers sit side by side. A close costing more than the sprint it certifies is reported as the defect it is.

## Recommendation

Cut before adding. The instinct this repo has followed for three releases is to answer a weak gate with another gate, and the result is the ceremony described above; the fix is subtraction. Take the nine chain steps and sort them into the two that gate and the rest that report - the sorting is most of the design work, and it should be done with the operator, since which defects are stop-ships is their judgement and not a rule.

Sequence CR0506 first: without a route from a repaired REJECT back to covered, the goal gate cannot be cleared by the ordinary review loop, which is what deadlocked this very close.

Check during refine whether this SUBSUMES CR0505 rather than sitting beside it. CR0505 asks for a compulsory checklist and a sprint report, which was the right response to the state at the time; if the close gates on two questions and reports the rest, then CR0505's report IS that report and its checklist mostly evaporates. Two overlapping close-time documents is the drift this repo keeps filing bugs about, and shipping both would be a third instance.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Darren Benson (operator), from the RUN-01KYPZ1G close | Raised |
