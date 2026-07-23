# EP0150: A deterministic retitle path

> **Status:** In Progress
> **Derived Point Total:** 8
> **Parent:** CR0406
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0406. Delivers the work CR0406 requested.

## Story Breakdown

- [ ] [US0398: an atomic retitle of the H1, the filename slug and the index row, refusing before any write if any cannot be updated](../stories/US0398-an-atomic-retitle-of-the-h1-the-filename.md)
- [ ] [US0399: inbound references are rewritten or named via check_links, and the retitle is recorded on the artefact](../stories/US0399-inbound-references-are-rewritten-or-named-via-check.md)

## Acceptance Criteria (Epic Level)

- [ ] A deterministic retitle exists that changes the H1, the filename slug and the index row link text as one operation, refusing before any write if any of the three cannot be updated.
- [ ] Inbound references are found and rewritten, or the retitle refuses and NAMES them - never rewrites the artefact and leaves the references dangling.
- [ ] A retitle is recorded on the artefact, so a reader can see the title changed and what it was, rather than finding a filename that disagrees with git history for no stated reason.
- [ ] Where a retitle is refused, the message states the reason and what to do, in the manner the grooming refusal already sets.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
