# EP0154: Sequential or parallel delivery, chosen at run start

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0411
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0411. Delivers the work CR0411 requested.

## Story Breakdown

- [ ] [US0407: a conditional prompt offers SEQUENTIAL or PARALLEL only when a genuine file-disjoint decomposition exists, and records the chosen mode](../stories/US0407-a-conditional-prompt-offers-sequential-or-parallel-only.md)
- [ ] [US0408: the disjointness check counts test files as coupling](../stories/US0408-the-disjointness-check-counts-test-files-as-coupling.md)
- [ ] [US0409: the choice is deterministic and the plan states the mode and why the alternative was or was not available](../stories/US0409-the-choice-is-deterministic-and-the-plan-states.md)

## Acceptance Criteria (Epic Level)

- [ ] sprint plan, at run start, offers the operator a SEQUENTIAL or PARALLEL delivery mode when the batch has a genuine file-disjoint decomposition, and records the chosen mode on the run.
- [ ] The parallel option is offered ONLY when a real parallel decomposition exists: more than one unit, at least two clusters with disjoint file sets, and the dependency waves permit concurrency. A one-unit batch, an all-coupled batch, or a pure dependency chain is delivered sequentially and the prompt says why parallel was not offered.
- [ ] The file-disjointness that decides parallelisability counts TEST files as coupling, not only source - this run's one merge conflict came from excluding them, and two agents editing the same test file conflict exactly as two editing the same module do.
- [ ] The decision is deterministic: the same batch and repo state offer the same choice every time, computed from the shared-file clusters and dependency waves sprint plan already derives, not from agent judgement.
- [ ] The chosen mode is recorded on the run state and stated in the plan output, so a reader can see which mode a run used and why the alternative was or was not available.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
