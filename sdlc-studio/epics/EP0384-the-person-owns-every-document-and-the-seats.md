# EP0384: The person owns every document, and the seats check the work under delegated authority

> **Status:** Draft
> **Derived Point Total:** 4
> **Parent:** CR0755
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0755. Delivers the work CR0755 requested.

## Story Breakdown

- [ ] [US1339: The skill says the person owns the PRD and the PVD, and the seat checks the work under delegated authority](../stories/US1339-the-skill-says-the-person-owns-the-prd.md)
- [ ] [US1340: A seat corrects a fact in the document it reviews against and proposes any change to what it requires](../stories/US1340-a-seat-corrects-a-fact-in-the-document.md)

## Acceptance Criteria (Epic Level)

- [ ] Given the skill's reference files, then no seat is said to own the PRD or the PVD: the person owns each, and the seat is accountable, with delegated authority, for checking the work satisfies it and signs its review leg. Fails on: "owned by the Product Owner seat", "The Product Owner seat owns this", or a table column headed Owns that names a seat.
- [ ] Given the same files, then a seat still never authors a document it reviews against: it proposes a change and the person makes it. Fails on: a seat said to edit the PRD or PVD whose review leg it signs.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
