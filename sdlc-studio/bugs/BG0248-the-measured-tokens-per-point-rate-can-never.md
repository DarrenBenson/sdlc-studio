# BG0248: The measured tokens-per-point rate can never advance while sprints are interactive: the join needs per-unit actuals no interactive sprint writes

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/lib/telemetry.py,.claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The plan reports 'this project has 3 unit(s) of its own evidence so far; the rate becomes ITS measurement at 5'. That counter has been stuck at 3 for months and structurally CANNOT advance. `tokens_per_point` joins the plan-time forecast log against the PER-UNIT actuals log; an interactive sprint has no runner and writes no per-unit actual, so it contributes nothing however well it is measured at sprint level. Measured directly on this repo: 208 forecast records carry plan-time points, and exactly 3 have a non-zero per-unit actual - CR0268, CR0269 and CR0270, all from the runner era. Every sprint since has been interactive. The consequence is that the estimator will use the shipped seed constant for ever while telling the operator, in every plan, that it is two units away from owning its own rate. That sentence is the problem: it presents a permanent state as an imminent one. IMPORTANT CORRECTION, because this bug exists partly to fix a false claim: BG0246's summary and decision D0047's rationale both asserted that `batch_history`'s filter was what stalled this counter. That is WRONG. They are different sources - `batch_history` reads the velocity table, `tokens_per_point` reads the telemetry logs - and fixing BG0246 correctly left the counter at 3, exactly as it should have. The claim was written by the sprint author without checking, in a bug about numeric honesty, and was caught independently by the implementing agent and by the author before review.

## Steps to Reproduce

1. Run sprint.py plan against any batch. 2. Read the rate line: 'this project has 3 unit(s) of its own evidence so far; the rate becomes ITS measurement at 5'. 3. Close an interactive sprint, however well measured at sprint level, and re-run the plan. Observed: the counter is still 3. Confirm the cause directly by joining lib/telemetry.py's forecasts() and actuals(): 208 forecast records with points, 3 with a non-zero per-unit actual, all pre-dating the interactive era.

## Proposed Fix

Decide where the rate should be MEASURED FROM, which is the question neither D0047 nor BG0246 ruled on. Two candidates worth weighing. Either let a sprint-level actual contribute at sprint granularity - total tokens over total delivered points, one contribution per sprint rather than per unit - which is the same trade D0047 already accepted for `batch_history`, with the same caveat that per-unit variance is hidden. Or attribute the sprint delta across its units at close, which is more precise in appearance and less honest in substance, since the split would be invented rather than observed. Whichever is chosen, the reported sentence must stop promising an imminent transition that cannot occur: if the rate cannot advance under the current way of working, the plan should say THAT rather than count towards a threshold it will never reach. Guard it with a test that feeds a sprint-level-only history and asserts the reported text does not claim the project is N units from its own rate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
