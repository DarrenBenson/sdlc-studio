# EP0203: The routine backlog question is answered by the tooling, and a review's findings never cross a shell

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0516
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0516. Delivers the work CR0516 requested.

## Story Breakdown

- [ ] [US0614: A points census answers how much is left by status and by type, so the routine question is not answered by a script written on the spot](../stories/US0614-a-points-census-answers-how-much-is-left.md)
- [ ] [US0615: sprint review-batch takes its findings from a fields-file, so prose carrying backticks is stored verbatim rather than executed](../stories/US0615-sprint-review-batch-takes-its-findings-from-a.md)

## Acceptance Criteria (Epic Level)

- [ ] `review-batch --fields-file` stores a findings document containing backticks and `$(` verbatim, proven by reading the recorded row back and comparing byte-for-byte with the input
- [ ] A findings string passed through the shell is no longer the only path, and the help names the fields-file as the way to record text carrying shell metacharacters
- [ ] A single command answers how many points remain in the delivery backlog, split by status and by type, and excludes terminal statuses - proven against a fixture containing one `Won't Implement` unit, which must not be counted
- [ ] The points census agrees with `sprint plan`'s total over the same unit set, so two readers cannot report different sizes for one backlog

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
