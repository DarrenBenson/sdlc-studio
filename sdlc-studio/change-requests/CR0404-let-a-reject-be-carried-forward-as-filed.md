# CR-0404: Let a REJECT be carried forward as filed findings, reusing the file-a-finding-or-waive idiom the review already mandates for legs

> **Status:** Complete
> **Decomposed-into:** EP0113
> **Parent:** RFC0052
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/conformance.py,.claude/skills/sdlc-studio/reference-review.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator observation at the RUN-01KY3MFX close, filed by Claude Opus 4.8

## Summary

Operator observation at the RUN-01KY3MFX close, and the precedent is already in the shipped guidance. reference-review.md line 69 resolves a missing required review LEG one of exactly two ways - file a finding, which is the default, or record an explicit waiver - and forbids resolving it by narrative downgrade to optional. That is fail-forward, already stated, already enforced (`review_prep.required_legs` makes it machine-visible and `gate --release` refuses an absent-and-unwaived leg). The same idiom is NOT available for a sprint-review VERDICT. A REJECT blocks: `conformance.sprint_covers_independently` accepts a sprint-level review as evidence only on an APPROVE, so there is no path that says 'these findings are real, they are filed as bugs, the sprint carries on'. RUN-01KY3MFX is the measurement. Ten adversarial rounds. The CODE converged at round 7, which found zero defects in logic and said so. Rounds 8, 9 and 10 were prose - counts, superlatives, an enumeration wrong at three, four, five, six and seven - each round's findings created by the previous round's repair. Every one of those findings was worth having and none of them needed to block. Under a fail-forward policy the sprint closes at round 7 with the prose findings filed as bugs, which is exactly what happened in the end anyway, minus three rounds. This is a genuine preference difference rather than a defect: some teams want the loop to run until it is clean, and some want the findings on the backlog and the sprint shipped. The project currently only supports the first, and does not say so.

## Impact

Every closing review. Today a project whose deliverable includes prose can loop indefinitely, because prose has no executable oracle and an adversary will essentially always find something - the round count is bounded by patience rather than by convergence. The cost is measurable: rounds on this sprint ran roughly 100,000 to 200,000 tokens each, and three of ten bought only prose findings that a filed bug would have carried just as well.

## Acceptance Criteria

- [ ] A project can declare a review policy: block on REJECT (today's behaviour, and the default so nothing changes), or carry forward - the findings are FILED as artefacts and the sprint proceeds.
- [ ] Under carry-forward, every finding must be filed or explicitly waived with a reason, exactly as a missing review leg already is. Narrative downgrade is refused in both cases.
- [ ] The close records which policy was in force and lists the findings carried, so a reader can tell a sprint that converged from one that carried findings forward.
- [ ] A carried-forward finding is linked to the units it was found against, so it cannot be lost when the sprint closes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | Darren Benson | Raised |
