# EP0182: A review round records how long it took, so the overhead ratio stops being a floor

> **Status:** Done
> **Derived Point Total:** 6
> **Parent:** CR0466
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0466. Delivers the work CR0466 requested.

## Story Breakdown

- [x] [US0534: A recorded review round carries a duration, and a round recorded without one says so rather than counting as zero](../stories/US0534-a-recorded-review-round-carries-a-duration-and.md)
- [x] [US0535: The overhead ratio consumes recorded review durations, and states it is a lower bound only while a component is genuinely unmeasured](../stories/US0535-the-overhead-ratio-consumes-recorded-review-durations-and.md)

## Acceptance Criteria (Epic Level)

- [ ] The behaviour in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
