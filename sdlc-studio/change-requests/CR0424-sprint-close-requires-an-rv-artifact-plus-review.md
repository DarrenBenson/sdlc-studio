# CR-0424: sprint close requires an RV artifact plus review_prep stamp even after critic sprint-review already recorded the APPROVE

> **Status:** Proposed
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
