# EP0089: The close reports every blocker in one pass

> **Status:** Done
> **Derived Point Total:** 8
> **Parent:** CR0359
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0359. Delivers the work CR0359 requested.

## Story Breakdown

- [x] [US0273: a standalone preflight reports every unmet close prerequisite in one read-only pass](../stories/US0273-a-standalone-preflight-reports-every-unmet-close-prerequisite.md)
- [x] [US0274: the preflight covers the apply-signoff prerequisites per unit, not just the gate lanes](../stories/US0274-the-preflight-covers-the-apply-signoff-prerequisites-per.md)
- [x] [US0275: sprint close runs the preflight before executing any step, so nothing is discovered serially](../stories/US0275-sprint-close-runs-the-preflight-before-executing-any.md)

## Acceptance Criteria (Epic Level)

- [ ] sprint close runs a pre-flight that reports EVERY unmet prerequisite in one pass before executing any step
- [ ] the pre-flight covers the apply-signoff prerequisites (a recorded critic verdict, an independent principal) alongside the existing gate lanes
- [ ] the pre-flight is available standalone so it can be run before starting a close

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
