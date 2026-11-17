# EP0329: One command writes a unit's changelog fragment from its title and acceptance criteria

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0676
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0676. Delivers the work CR0676 requested.

## Story Breakdown

- [ ] [US1206: An artifact changelog command writes a unit's fragment in the shape the changelog-shape lane passes](../stories/US1206-an-artifact-changelog-command-writes-a-unit-s.md)
- [ ] [US1207: Lane land writes the fragment when the hand-in has none, keeps a hand edit, and the brief names the command](../stories/US1207-lane-land-writes-the-fragment-when-the-hand.md)

## Acceptance Criteria (Epic Level)

- [ ] `artifact.py changelog <id>` writes changelog.d/<id>.md from the unit's title and acceptance-criteria headlines in the shape the changelog-shape lane reads, and the lane passes it unedited.
- [ ] `sprint.py lane land` writes the fragment when the hand-in has none, and the lane brief names the command instead of describing the format.
- [ ] A hand edit to a generated fragment is kept, and the changelog-shape lane still refuses a malformed hand-written fragment.
- [ ] Before and after: on the next sprint builders make at most 2 changelog.d calls per unit against run six's 5.8 (76 over 13).

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
