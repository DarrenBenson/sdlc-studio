# EP0365: Every composed CHANGELOG entry names the unit its fragment was filed for

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0728
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0728. Delivers the work CR0728 requested.

## Story Breakdown

- [ ] [US1288: Compose writes each fragment's unit id into its entry exactly once, and the dry run reports the same ids](../stories/US1288-compose-writes-each-fragment-s-unit-id-into.md)
- [ ] [US1289: The release cut reports every fragment folded without a unit id, and the script catalogue describes the id carry](../stories/US1289-the-release-cut-reports-every-fragment-folded-without.md)

## Acceptance Criteria (Epic Level)

- [ ] When compose runs with apply, each top-level entry it folds carries the unit id taken from its fragment's file name, in one fixed place in the entry, unless the entry text already names that id
- [ ] A fragment whose file name is not a unit id is folded without an id and compose reports it, so the gap is visible at the cut
- [ ] The compose dry run reports the same ids it would write and changes nothing
- [ ] A test in `test_changelog.py` composes two fixture fragments, one naming its id in the prose and one not, and asserts each resulting entry names its unit id exactly once

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
