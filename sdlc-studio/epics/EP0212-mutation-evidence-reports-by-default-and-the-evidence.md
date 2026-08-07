# EP0212: Mutation evidence reports by default, and the evidence a measured run produces is the evidence the gate reads

> **Status:** Draft
> **Derived Point Total:** 16
> **Parent:** CR0537
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0537. Delivers the work CR0537 requested.

## Story Breakdown

- [ ] [US0660: A surviving mutant becomes a severity-rated bug and the transition proceeds, and the run names the mode that held it](../stories/US0660-a-surviving-mutant-becomes-a-severity-rated-bug.md)
- [ ] [US0661: A measured mutation run records what it applied, attributed to a unit, so the gate is satisfiable by measurement rather than only by self-report](../stories/US0661-a-measured-mutation-run-records-what-it-applied.md)

## Acceptance Criteria (Epic Level)

- [ ] `review.mutation_evidence` takes `report` (the DEFAULT), `block`, or `off`, and the resolved value is printed by the close so nobody has to guess which mode a run was held to
- [ ] In `report` mode a surviving mutant is FILED as a bug through the shipped filer - naming the unit, the criterion, the mutant and the test that failed to kill it - and the close PROCEEDS; nothing about the run is held
- [ ] A filed survivor carries a derived severity rather than a uniform one, so triage has something to sort on: a survivor on a refusal or gate path outranks one on a reporting path, which outranks one on prose
- [ ] `block` remains available and behaves exactly as today, so a project that wants the hard bar keeps it by setting one value
- [ ] The retro counts survivors filed, by severity, so the trade being made is visible over time rather than felt
- [ ] Re-filing is idempotent: the same surviving mutant on the same unit does not mint a second bug on the next run
- [ ] One thing still blocks in every mode: a mutant RECORDED as killed that is shown to survive. That is not a quality bar, it is the ledger lying about itself, and this run produced exactly one

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
