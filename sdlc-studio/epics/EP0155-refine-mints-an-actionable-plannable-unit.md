# EP0155: refine mints an actionable, plannable unit

> **Status:** Done
> **Derived Point Total:** 10
> **Parent:** CR0412
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0412. Delivers the work CR0412 requested.

## Story Breakdown

- [x] [US0410: refine requires or inherits an Affects per story so a minted story is plannable, refusing or seeding-for-confirmation where none is given](../stories/US0410-refine-requires-or-inherits-an-affects-per-story.md)
- [x] [US0411: a refined story's AC block is labelled a grooming placeholder, not left as content, so the ungroomed count is machine-visible](../stories/US0411-a-refined-story-s-ac-block-is-labelled.md)
- [x] [US0412: reference-cr.md and reference-rfc.md state refine produces a plannable unit whose ACs still need grooming, opt-out per project](../stories/US0412-reference-cr-md-and-reference-rfc-md-state.md)

## Acceptance Criteria (Epic Level)

- [ ] refine REQUIRES an Affects per story (or a per-story way to inherit and narrow the parent request's Affects), so a minted story is plannable the moment it exists - `sprint plan` does not refuse it as ungroomed.
- [ ] Where the caller supplies no Affects, refine either refuses with a message naming what to add (the grooming-refusal idiom), or seeds a defensible Affects from the parent request and marks it for confirmation - it does NOT silently mint an unplannable unit.
- [ ] The acceptance-criteria block a refined story carries is honestly labelled as a grooming placeholder, not left as `{{placeholder}}` that reads as content - so a reader can tell a groomed story from an ungroomed one at a glance, and the count of ungroomed units is machine-visible.
- [ ] reference-cr.md / reference-rfc.md state that refine produces a PLANNABLE unit (Affects present) whose ACs still need grooming, so the two-backlog promise - a refined request is delivery work - is true rather than aspirational.
- [ ] The behaviour is chosen deliberately per project: a project that wants the old lenient behaviour can opt out, but the default makes refine output actionable.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
