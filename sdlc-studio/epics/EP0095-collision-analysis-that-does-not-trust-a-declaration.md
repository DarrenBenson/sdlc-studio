# EP0095: Collision analysis that does not trust a declaration

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0347
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0347. Delivers the work CR0347 requested.

## Story Breakdown

- [ ] [US0291: Derive shared-file clusters from the files a unit's ACs and verifiers name, not Affects alone](../stories/US0291-derive-shared-file-clusters-from-the-files-a.md)
- [ ] [US0292: Report an Affects line the unit's own content contradicts, at plan time](../stories/US0292-report-an-affects-line-the-unit-s-own.md)

## Acceptance Criteria (Epic Level)

- [ ] the collision analysis includes the test files a unit will touch, not only its declared Affects
- [ ] a unit whose declared Affects does not resolve on disk, or omits a file its ACs name, is reported at plan time rather than at grooming

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
