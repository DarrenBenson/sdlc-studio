# EP0235: The lane-check corpus can only shrink

> **Status:** Draft
> **Derived Point Total:** 13
> **Parent:** CR0539
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0539. Delivers the work CR0539 requested.

## Story Breakdown

- [ ] [US0769: lane-check records the corpus count as a baseline and REFUSES an increase](../stories/US0769-lane-check-records-the-corpus-count-as-a.md)
- [ ] [US0770: The baseline falls automatically when a unit is repaired, and rises only by recorded decision](../stories/US0770-the-baseline-falls-automatically-when-a-unit-is.md)
- [ ] [US0771: A unit under construction sees its OWN lane-check line at delivery, not the corpus total](../stories/US0771-a-unit-under-construction-sees-its-own-lane.md)

## Acceptance Criteria (Epic Level)

- [ ] lane-check records the corpus count as a baseline and refuses an INCREASE, so a new unit cannot add a criterion that never enters its own command while 181 existing ones stay reported.
- [ ] The baseline falls when a unit is repaired and never rises silently: lowering it is automatic, raising it needs a recorded decision.
- [ ] A unit under construction sees its OWN lane-check line at delivery, not only the corpus total - a report of 181 is background noise, a report of one is a finding.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
