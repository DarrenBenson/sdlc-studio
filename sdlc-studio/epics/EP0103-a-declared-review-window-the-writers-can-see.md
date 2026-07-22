# EP0103: A declared review window the writers can see

> **Status:** Done
> **Derived Point Total:** 8
> **Parent:** CR0388
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0388. Delivers the work CR0388 requested.

## Story Breakdown

- [x] [US0307: A mutation or review window is declared on disk and skill scripts refuse or warn while it is open](../stories/US0307-a-mutation-or-review-window-is-declared-on.md)
- [x] [US0308: The commit path refuses to stage files outside the declared change set while a window is open](../stories/US0308-the-commit-path-refuses-to-stage-files-outside.md)

## Acceptance Criteria (Epic Level)

- [ ] The reviewer declares a mutation window, and the author's commit path refuses or warns while one is open
- [ ] Staging is scoped rather than wholesale during a review: a documented path that commits named paths instead of `git add -A`
- [ ] reference-sprint.md states the hazard where it states the single-writer rule for mutation runs, so the review-time case is covered by the same discipline
- [ ] A test drives the guard with a mutation window open and a green-but-mutated source, and asserts the commit is refused - the case the gate cannot catch today

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
