# EP0189: The close costs less than the work it certifies: earn the gate verdict once, record a batch in one call, and refuse in one pass

> **Status:** Draft
> **Derived Point Total:** 32
> **Parent:** CR0498
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0498. Delivers the work CR0498 requested.

## Story Breakdown

- [ ] [US0553: A close-phase commit over an unchanged test-relevant surface reuses the gate verdict the close itself earned, rather than re-running the suites](../stories/US0553-a-close-phase-commit-over-an-unchanged-test.md)
- [ ] [US0554: A listing-only declaration names the ids its structural read depends on, so filing an artefact stops triggering the full suites](../stories/US0554-a-listing-only-declaration-names-the-ids-its.md)
- [ ] [US0555: sprint close --dry-run reports every unmet prerequisite of all seven steps in one read-only pass, retro content included, and writes nothing](../stories/US0555-sprint-close-dry-run-reports-every-unmet-prerequisite.md)
- [ ] [US0556: critic evidence, record and signoff each record a whole batch in one invocation, with the open run as the default scope](../stories/US0556-critic-evidence-record-and-signoff-each-record-a.md)
- [ ] [US0557: A batch invocation missing a required argument is refused once before any unit is written, naming every argument the command needs](../stories/US0557-a-batch-invocation-missing-a-required-argument-is.md)
- [ ] [US0558: A retro created by the scaffold and filled in as its template demonstrates passes retro validate without a rejection round-trip](../stories/US0558-a-retro-created-by-the-scaffold-and-filled.md)
- [ ] [US0559: The close reports its own cost - gate seconds and elapsed - so the next reduction is measured against a number rather than an impression](../stories/US0559-the-close-reports-its-own-cost-gate-seconds.md)

## Acceptance Criteria (Epic Level)

- [ ] `sprint close --dry-run` reports every unmet prerequisite of all seven steps in one read-only pass, retro content included, and writes nothing.
- [ ] The adversarial evidence, the verdict and the sign-off can each be recorded for a whole batch in one invocation, with the open run as the default scope.
- [ ] A required argument missing from a batch invocation is refused once, before any unit is written, naming every argument the command needs.
- [ ] A retro created by the scaffold and filled in as the template demonstrates passes `retro validate` without a rejection round-trip.
- [ ] A close-phase commit that touches no script, template or tool reuses the gate verdict the close itself earned, rather than re-running the suites.
- [ ] The close reports its own cost - gate seconds and elapsed - so the next reduction is measured against a number rather than an impression.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
