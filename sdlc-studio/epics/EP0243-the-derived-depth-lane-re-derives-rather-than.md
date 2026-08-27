# EP0243: The derived-depth lane re-derives, rather than trusting each span's own seal

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0558
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0558. Delivers the work CR0558 requested.

## Story Breakdown

- [ ] [US0801: A unit whose stamped derived half no longer matches a fresh derivation is REPORTED with both fingerprints](../stories/US0801-a-unit-whose-stamped-derived-half-no-longer.md)
- [ ] [US0802: A unit whose span matches a fresh derivation is passed silently - the paired control](../stories/US0802-a-unit-whose-span-matches-a-fresh-derivation.md)
- [ ] [US0803: An eviction of a unit's ledger rows is visible from the lane's output alone](../stories/US0803-an-eviction-of-a-unit-s-ledger-rows.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a unit whose stamped derived half no longer matches a fresh derivation, when the `derived-depth` lane runs, then that unit is REPORTED by name with both fingerprints - a seal proves only that the span was not hand-edited, and says nothing about whether the evidence behind it still exists
- [ ] Given a unit whose stamped span matches a fresh derivation, when the lane runs, then it is silent about that unit - the paired control, so the lane does not become a warning that always fires and is therefore never read
- [ ] Given a corpus in which some unit's ledger rows were evicted by a later registration against the same target file, when the lane runs, then the eviction is visible from the lane's output alone, without anyone thinking to ask `verify_ac.py depth` about that particular unit

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
