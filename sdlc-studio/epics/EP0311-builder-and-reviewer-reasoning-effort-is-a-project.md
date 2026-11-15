# EP0311: Builder and reviewer reasoning effort is a project setting, stamped on each planned unit and stated in the run's report

> **Status:** Done
> **Derived Point Total:** 6
> **Parent:** CR0699
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0699. Delivers the work CR0699 requested.

## Story Breakdown

- [x] [US1165: A project sets builder and reviewer reasoning effort; the plan stamps it on each unit, the lane brief names it, and a reviewer below its builder is refused without a recorded decision](../stories/US1165-a-project-sets-builder-and-reviewer-reasoning-effort.md)
- [x] [US1166: Each run's report of record states the effort each builder and reviewer was dispatched at, read from the run record](../stories/US1166-each-run-s-report-of-record-states-the.md)

## Acceptance Criteria (Epic Level)

- [ ] A project can set the reasoning effort for builders and for reviewers separately (default: inherit, today's behaviour), and a sprint wave dispatches each agent at the effort set
- [ ] Each run record and sprint report states the effort each builder and reviewer ran at
- [ ] A trial compares low against medium for builders, first on the bench fixtures (tools/bench) and then on one run's comparable units, reporting priced tokens per point, review rounds, rejections and the held-back suite score; the keep rule is recorded as a decision before the trial starts and the result is recorded against it
- [ ] A reviewer's effort is never set below its builder's without a recorded decision, as `routing.critic_tier` never makes the critic a smaller tier than the author

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
