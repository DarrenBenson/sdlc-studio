# CR-0424: sprint close requires an RV artifact plus review_prep stamp even after critic sprint-review already recorded the APPROVE

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Decomposed-into:** EP0171
> **Priority:** Low
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/review_prep.py,.claude/skills/sdlc-studio/scripts/critic.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Closing EP0163 with an already-recorded critic sprint-review (APPROVE over the batch) still failed the review-current lane until a separate RV artifact was created and `review_prep` close stamped LATEST.md. One adversarial review has to be entered twice across two record surfaces before the close accepts it.

## Impact

Every two-role close pays a double-entry tax: the reviewer verdict is recorded once as a sprint-review and again as an RV plus anchor. Extra steps that are easy to get subtly wrong on the hot close path CR0421 just worked to smooth.

## Acceptance Criteria

- [ ] A recorded critic sprint-review APPROVE covering the batch can satisfy the close review-current lane directly, or the close derives the RV and anchor from it, so the review is entered once

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Raised |
| 2026-09-15 | backlog sweep 2026-09-15 | Backlog sweep 2026-09-15: residue confirmed by fixture - gate._batch_is_independently_covered reads only per-unit verdicts (critic.verdict_for), so a batch covered by a sprint-review APPROVE (what sprint review-batch, the close's own remedy, writes) still reads blocking in the review-current lane, while sprint.review_coverage accepts the same record. Per-unit coverage was fixed by US0608. Cheaper fix than deriving an RV: let the lane read sprint_review_for. |
| 2026-09-21 | audit ruling | still wanted, correctly in progress. The double-entry tax is half-relieved and half-live: `gate._batch_is_independently_covered` passes a PER-UNIT row where a SPRINT-review row is expected, so a batch covered solely by a recorded sprint-review APPROVE still blocks, while `critic.coverage_state` already has the correct fallback and the lane does not use it. Children US0474/US0475 are Ready but unbuilt, which is what In Progress means here. Noted: this is itself a live instance of CR0504's divergent-reader class, and a one-line fix independent of its children. |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - RV artefact + review_prep: US0876 one-pass close; sprint-review ledger deleted in batch 2 |
