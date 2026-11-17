# EP0334: Three shipped steps stop leaving state that the next step refuses

> **Status:** Draft
> **Derived Point Total:** 6
> **Parent:** CR0683
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0683. Delivers the work CR0683 requested.

## Story Breakdown

- [ ] [US1224: Lane land checks the handed-in self-check claims before it commits, and the brief names one fragment label](../stories/US1224-lane-land-checks-the-handed-in-self-check.md)
- [ ] [US1225: A verify run in a lane worktree changes no file outside the unit's Affects](../stories/US1225-a-verify-run-in-a-lane-worktree-changes.md)
- [ ] [US1226: Filing a child under a parent request updates the parent's spawned work cell in the same write](../stories/US1226-filing-a-child-under-a-parent-request-updates.md)

## Acceptance Criteria (Epic Level)

- [ ] `lane land` validates the hand-in's self-check claims before it commits and refuses with the offending label, leaving no commit, and the lane brief names one label for a fragment claim; a fixture with US1122's CHANGELOG labels is refused before any commit.
- [ ] `verify_ac run` in a lane worktree changes no file outside the unit's Affects: after a fixture run, `git status --porcelain` lists nothing outside them.
- [ ] `file_finding --parent <RFC>` and `artifact.py new --parent <RFC>` each update the parent's spawned-work cell in the same write, so `reconcile --dry-run` reports no drift after filing.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
