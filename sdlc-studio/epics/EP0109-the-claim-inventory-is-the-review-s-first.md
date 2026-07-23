# EP0109: The claim inventory is the review's first pass, not its last

> **Status:** Done
> **Derived Point Total:** 8
> **Parent:** CR0393
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0393. Delivers the work CR0393 requested.

## Story Breakdown

- [x] [US0320: The reviewer brief directs a first pass enumerating every assertion in Resolutions, docstrings, comments and CHANGELOG entries, marked TRUE, FALSE or UNVERIFIABLE](../stories/US0320-the-reviewer-brief-directs-a-first-pass-enumerating.md)
- [x] [US0321: A claim that cannot be checked mechanically is reported UNVERIFIABLE rather than assumed true, so the reader sees how much prose rests on trust](../stories/US0321-a-claim-that-cannot-be-checked-mechanically-is.md)
- [x] [US0322: The claim pass runs BEFORE the logic review and reports separately, so a prose-only round is visibly a different kind of round](../stories/US0322-the-claim-pass-runs-before-the-logic-review.md)

## Acceptance Criteria (Epic Level)

- [ ] The reviewer brief directs an explicit first pass that enumerates every assertion in the diff's Resolutions, docstrings, comments and CHANGELOG entries, and marks each TRUE, FALSE or UNVERIFIABLE against the code.
- [ ] A claim that cannot be checked mechanically is reported as UNVERIFIABLE rather than assumed true, so the reader can see how much of the prose rests on trust.
- [ ] The pass runs BEFORE the logic review and its findings are reported separately, so a round that finds only prose defects is visibly a different kind of round from one that finds logic defects.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
