# EP0214: The two paths a user arrives on are rehearsed through the shipped CLI, on a tree that must fail before the repairs land

> **Status:** Done
> **Derived Point Total:** 13
> **Parent:** CR0542
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0542. Delivers the work CR0542 requested.

## Story Breakdown

- [x] [US0664: A greenfield fixture is built from nothing and driven through init run to a written sprint plan, and the lane reddens when that path is broken](../stories/US0664-a-greenfield-fixture-is-built-from-nothing-and.md)
- [x] [US0665: A v4-era fixture is driven through migrate --apply to a GREEN gate, asserting the upgrade's outcome rather than the migrate's report](../stories/US0665-a-v4-era-fixture-is-driven-through-migrate.md)
- [x] [US0666: The rehearsal runs as a gate lane at the push and release boundaries, with its cost recorded and its fixtures proven to write outside the working tree](../stories/US0666-the-rehearsal-runs-as-a-gate-lane-at.md)

## Acceptance Criteria (Epic Level)

- [ ] A gate lane builds a greenfield fixture from nothing via `init run`, drives it through `sprint plan --write` and asserts a run was opened, reading the process exit code directly rather than through a pipe
- [ ] The same lane builds a v4-era fixture, runs `migrate --apply` and then `gate.py`, and asserts the gate is GREEN - the upgrade's outcome, not the migrate's report
- [ ] Both fixtures are constructed fresh per run in a temporary directory outside the repository, and a test proves the lane fails if a fixture write lands inside the working tree (BG0536's shape)
- [ ] The lane is proven to FAIL on a tree carrying BG0558, BG0559 or BG0560 unrepaired, by reverting each repair in turn and asserting the lane reddens - the positive control, without which the lane's green means nothing
- [ ] The lane is bound to the push and release boundaries rather than to every commit, and its measured cost is recorded against the gate budget

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Created via `new` (deterministic) |
