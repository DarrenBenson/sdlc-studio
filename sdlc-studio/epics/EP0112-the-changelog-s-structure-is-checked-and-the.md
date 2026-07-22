# EP0112: The CHANGELOG's structure is checked, and the hand-edit path is made visibly wrong

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0405
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0405. Delivers the work CR0405 requested.

## Story Breakdown

- [ ] [US0330: A structural check fails on subsection headings out of order, duplicated within one release, or empty - the shapes a bad hand-insert produces](../stories/US0330-a-structural-check-fails-on-subsection-headings-out.md)
- [ ] [US0331: The structural check joins the gate lane that already binds changelog fragments, and a hand-edit of Unreleased while changelog.d is live is made visibly wrong](../stories/US0331-the-structural-check-joins-the-gate-lane-that.md)

## Acceptance Criteria (Epic Level)

- [ ] A structural check fails when a release section's subsection headings are out of order, duplicated within one release, or when a subsection is empty - the shapes a bad hand-insert produces. This is the one criterion the filing got right and nothing covers.
- [ ] The structural check runs in the existing gate. Note the gate already binds `changelog-fragments` at a release cut (`gate.py`:1252); the structural check joins that lane rather than inventing one.
- [ ] While `changelog.d/` is live, a hand-edit of `CHANGELOG.md`'s `[Unreleased]` section is made visibly wrong rather than merely discouraged - the step that would have prevented both RUN-01KY3MFX incidents, and the one the original filing missed because it did not check whether the helper existed.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
