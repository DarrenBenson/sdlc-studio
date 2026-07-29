# EP0172: Dead surfaces: the supersession record, the epic-index columns and the flag that does nothing

> **Status:** Draft
> **Parent:** CR0437
> **Parent:** CR0436
> **Derived Point Total:** 10
> **Parent:** CR0434
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** S

## Summary

Decomposed from CR0434. Delivers the work CR0434 requested.

## Story Breakdown

- [ ] [US0476: RFC0009 records its partial supersession by RFC0038, to the RFC0034 convention, element by element](../stories/US0476-rfc0009-records-its-partial-supersession-by-rfc0038-to.md)
- [ ] [US0477: reconcile derives the epic index's Stories and Deps cells from the census and syncs them](../stories/US0477-reconcile-derives-the-epic-index-s-stories-and.md)
- [ ] [US0478: The mint path writes the canonical epic row, and the shipped template declares the same columns](../stories/US0478-the-mint-path-writes-the-canonical-epic-row.md)
- [x] [US0479: Delete gate's dead --verify-batch flag and the documentation claiming it does something](../stories/US0479-delete-gate-s-dead-verify-batch-flag-and.md)

## Acceptance Criteria (Epic Level)

- [ ] Decide once: either teach reconcile (and artifact.py epic wiring) to derive and maintain Stories/Deps from story-index parent links and epic Dependencies sections with a drift check, or drop the two columns from the template and all four indexes so the surface stops asserting data it does not hold.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
