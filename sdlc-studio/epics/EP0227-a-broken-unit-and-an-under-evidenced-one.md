# EP0227: A broken unit and an under-evidenced one get different verdicts

> **Status:** Draft
> **Derived Point Total:** 16
> **Parent:** CR0524
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0524. Delivers the work CR0524 requested.

## Story Breakdown

- [ ] [US0730: A verdict distinguishes a unit that does not work from one whose evidence cannot fail](../stories/US0730-a-verdict-distinguishes-a-unit-that-does-not.md)
- [ ] [US0731: Evidence debt is recorded against the CRITERION it attaches to, naming the surviving mutant](../stories/US0731-evidence-debt-is-recorded-against-the-criterion-it.md)
- [ ] [US0732: The batch summary reports the two counts separately](../stories/US0732-the-batch-summary-reports-the-two-counts-separately.md)
- [ ] [US0733: A unit carrying evidence debt is still refused a terminal status until it is cleared or deferred with a reason](../stories/US0733-a-unit-carrying-evidence-debt-is-still-refused.md)
- [ ] [US0734: The seat briefs tell a reviewer which verdict fits which finding, calibrated on RUN-01KYZKY5](../stories/US0734-the-seat-briefs-tell-a-reviewer-which-verdict.md)

## Acceptance Criteria (Epic Level)

- [ ] A verdict distinguishes a unit that does not work from one that works with evidence that cannot fail, and the second is not spelled REJECT
- [ ] Evidence debt is recorded against the CRITERION it attaches to, naming the mutant that survives, so a repair has a target rather than a whole unit to re-argue
- [ ] The batch summary reports the two counts separately, so a reader can see at a glance whether a run was broken or under-evidenced
- [ ] A unit carrying evidence debt is still refused a terminal status until the debt is cleared or explicitly deferred with a reason - the distinction changes the REPORT, never the bar
- [ ] The seat briefs tell a reviewer which verdict fits which finding, with the RUN-01KYZKY5 examples as the calibration, so the split is applied consistently rather than by each reviewer's taste

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
