# EP0094: A falsifiable estimator: the velocity record restored and enforced

> **Status:** Done
> **Derived Point Total:** 11
> **Parent:** CR0284
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0284. Delivers the work CR0284 requested.

## Story Breakdown

- [x] [US0288: close_owed treats a missing velocity row as an owed close item](../stories/US0288-close-owed-treats-a-missing-velocity-row-as.md)
- [x] [US0289: Backfill the velocity record from RETRO0029, marking unmeasurable rows as such](../stories/US0289-backfill-the-velocity-record-from-retro0029-marking-unmeasurable.md)
- [x] [US0290: Each plan re-measures the rate from the velocity record or names why it cannot](../stories/US0290-each-plan-re-measures-the-rate-from-the.md)

## Acceptance Criteria (Epic Level)

- [ ] The close-down enforcement (`close_owed` or the retro close gate) refuses/flags a sprint close whose accuracy/velocity write did not run when a token total is supplyable, with a recorded-override escape
- [ ] VELOCITY.md gains rows (or explicit unmeasured entries) for the closed sprints since RETRO0028 where totals are recoverable
- [ ] Plan output that quotes the tokens-per-point rate states its provenance (seed vs measured) and the RETRO0028 out-of-sample result rather than presenting the 25k seed as calibrated

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
