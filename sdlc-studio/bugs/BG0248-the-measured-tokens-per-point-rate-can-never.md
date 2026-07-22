# BG0248: The measured tokens-per-point rate can never advance while sprints are interactive: the join needs per-unit actuals no interactive sprint writes

> **Severity:** High
> **Points:** 3
> **Status:** Fixed
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/telemetry.py,.claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The plan reports 'this project has 3 unit(s) of its own evidence so far; the rate becomes ITS measurement at 5'. That counter has been stuck at 3 for months and structurally CANNOT advance. `tokens_per_point` joins the plan-time forecast log against the PER-UNIT actuals log; an interactive sprint has no runner and writes no per-unit actual, so it contributes nothing however well it is measured at sprint level. Measured directly on this repo: 208 forecast records carry plan-time points, and exactly 3 have a non-zero per-unit actual - CR0268, CR0269 and CR0270, all from the runner era. Every sprint since has been interactive. The consequence is that the estimator will use the shipped seed constant for ever while telling the operator, in every plan, that it is two units away from owning its own rate. That sentence is the problem: it presents a permanent state as an imminent one. IMPORTANT CORRECTION, because this bug exists partly to fix a false claim: BG0246's summary and decision D0047's rationale both asserted that `batch_history`'s filter was what stalled this counter. That is WRONG. They are different sources - `batch_history` reads the velocity table, `tokens_per_point` reads the telemetry logs - and fixing BG0246 correctly left the counter at 3, exactly as it should have. The claim was written by the sprint author without checking, in a bug about numeric honesty, and was caught independently by the implementing agent and by the author before review.

## Acceptance Criteria

- [x] **AC1:** With the per-unit evidence log verifiably EMPTY, the velocity record alone still
      yields a measured rate, so an interactive sprint can advance it.
      Pinned by `test_sprint.RateFromVelocityRecordTests.test_an_interactive_sprint_can_now_advance_the_rate`.
- [x] **AC2:** A velocity record spanning two models is REFUSED with its reason carried to the
      plan output, never averaged into a rate describing neither.
      Pinned by `test_sprint.RateFromVelocityRecordTests.test_a_rate_spanning_two_models_refuses_rather_than_averaging`.
- [x] **AC3:** A plan is never refused over a token estimate, whatever the rate source resolves
      to.
      Pinned by `test_sprint.RateFromVelocityRecordTests.test_a_rate_spanning_two_models_refuses_rather_than_averaging`.

## Steps to Reproduce

1. Run sprint.py plan against any batch. 2. Read the rate line: 'this project has 3 unit(s) of its own evidence so far; the rate becomes ITS measurement at 5'. 3. Close an interactive sprint, however well measured at sprint level, and re-run the plan. Observed: the counter is still 3. Confirm the cause directly by joining lib/telemetry.py's forecasts() and actuals(): 208 forecast records with points, 3 with a non-zero per-unit actual, all pre-dating the interactive era.

## Proposed Fix

Decide where the rate should be MEASURED FROM, which is the question neither D0047 nor BG0246 ruled on. Two candidates worth weighing. Either let a sprint-level actual contribute at sprint granularity - total tokens over total delivered points, one contribution per sprint rather than per unit - which is the same trade D0047 already accepted for `batch_history`, with the same caveat that per-unit variance is hidden. Or attribute the sprint delta across its units at close, which is more precise in appearance and less honest in substance, since the split would be invented rather than observed. Whichever is chosen, the reported sentence must stop promising an imminent transition that cannot occur: if the rate cannot advance under the current way of working, the plan should say THAT rather than count towards a threshold it will never reach. Guard it with a test that feeds a sprint-level-only history and asserts the reported text does not claim the project is N units from its own rate.

## Resolution

Fixed, and most of the fix belongs to US0290 rather than to this bug - recorded that way
because a Resolution claiming more than it did is the defect class this batch exists to attack.

**What was wrong, restated precisely.** `tokens_per_point` joined the plan-time forecast log
against the PER-UNIT actuals log. An interactive sprint has no runner and writes no per-unit
actual, so it contributed nothing however well it was measured. Measured on this repo: 208
forecast records carried plan-time points and exactly 3 had a non-zero per-unit actual - CR0268,
CR0269, CR0270, all from the runner era. Every sprint since has been interactive. The plan then
told the operator, every time, that it was two units away from owning its own rate. That sentence
was the harm: a permanent state presented as an imminent one.

**What actually fixed it.** US0290 changed the SOURCE. `tokens_per_point` now reads
`retro.measured_rate` over the velocity record first, falls back to the per-unit evidence log,
and reaches the seed last. The velocity record IS written by an interactive sprint, so the rate
can now advance. The misleading counter sentence is gone, replaced by a statement of what has
actually been measured plus the seed's own out-of-sample result.

**What this bug added.** The property US0290 implies was not directly pinned, so it is now:
`test_an_interactive_sprint_can_now_advance_the_rate` asserts that with the per-unit log
verifiably EMPTY (`telemetry.actuals(root) == {}`, the bug's exact premise) the velocity record
alone still yields a measured rate. Its sibling pins the refusal path.

**What is NOT fixed, and is not claimed to be.** This repo still plans at the seed. The velocity
record holds four rows carrying an actual: RETRO0028 at 56,407 tokens per point on
`claude-opus-4-8`, and RETRO0060, RETRO0061 and RETRO0065 totalling 79 points for 6,290,071
tokens - 79,621 per point - with the model UNRECORDED. `measured_rate` refuses a rate spanning
two models, correctly, because averaging them would describe neither. So the counter is no longer
stuck on a structural impossibility; it is blocked on a missing column, which is CR0373's scope
and is not in this batch. The models were NOT stamped retroactively from memory: inventing
provenance to make a number appear would be a worse defect than the one being fixed.

The `Affects` line above named `scripts/lib/telemetry.py`; the file is at `scripts/telemetry.py`.
Corrected here. It is the fifth wrong `Affects` found in this batch and the check that now
reports it is US0292, delivered alongside this bug.

Mutation-proven: 2 mutants on this bug's tests (the velocity source disabled; the refusal reason
suppressed into a silent seed), both killed, bytecode purged and the on-disk change asserted
before each verdict.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-22 | claude | Fixed - the rate's source moved to the velocity record (US0290); this bug pins the interactive-sprint property directly and records the residual model-column blocker as CR0373 |
