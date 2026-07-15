# BG0146: A recalibration relabels past falsifications as training error, erasing the evidence that caused it

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Effort:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py
> **Points:** 5
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`sample_class` labels a velocity row IN-SAMPLE when the CURRENT constants were fitted to that sprint actuals. But a row RATIO judges the estimator that MADE the forecast, not the one in force now. Conflating the two lets a recalibration rewrite the meaning of the history that justified it - which is BG0133 defect in a new form.

Concretely. RETRO0025 (0.55x) and RETRO0026 (0.39x) were forecast by base=50,000 tpc=600. Those constants were fitted to RETRO0024 six units ONLY; the RETRO0025 and RETRO0026 units were never in that fit. Both ratios were therefore GENUINE OUT-OF-SAMPLE FALSIFICATIONS, and they are the entire evidence base for dropping the per-unit forecast (CR0262).

CR0262 then fitted its new flat rate on those same actuals. `sample_class` now reads current-constants-were-fitted-to-these-actuals and labels both rows IN-SAMPLE, and the generated text asserts: "This ratio is TRAINING ERROR - it lands near 1.0x by construction and is not evidence the estimator works."

The text is self-refuting on its face. It sits directly above 0.39x. A training-error ratio hugs 1.0 by construction; 0.39x is the most decisive miss this project has recorded. The label and the number in the same table contradict each other, and the label is the one that is wrong.

TWO DISTINCT FACTS are being collapsed into one flag:
(a) the ratio judges the estimator that PRODUCED the forecast - for these rows, the old one, which was not fitted to them, so the ratio is honest evidence ABOUT THE OLD MODEL;
(b) the actuals are in the CURRENT model training set, so the row cannot VALIDATE THE CURRENT MODEL.
Both are true. The current label states (b) and silently destroys (a).

## Steps to Reproduce

1. python3 scripts/retro.py velocity. 2. Read: RETRO0025 0.55x [in-sample], RETRO0026 0.39x [in-sample]. 3. Open RETRO0026 accuracy block: "IN-SAMPLE: the constants in force were FITTED to these actuals. This ratio is TRAINING ERROR - it lands near 1.0x by construction." 4. The ratio printed two lines above is 0.39x. A training-error ratio cannot be 0.39x; the claim falsifies itself. 5. git log the same block before CR0262 landed: both rows read OUT-OF-SAMPLE, correctly.

## Proposed Fix

Class a row on TWO independent axes and print both, because they answer different questions. FORECAST ERA: was this row forecast by the constants now in force (out-of-sample), by an estimator since replaced (stale-constants), or by constants fitted to its own actuals (in-sample)? That axis governs what the RATIO means. FIT MEMBERSHIP: are this row actuals in the CURRENT model training set? That axis governs whether the row can VALIDATE the current model, and it must NOT overwrite the ratio meaning. RETRO0025 and RETRO0026 are stale-constants AND fitted: their 0.39x and 0.55x remain honest evidence about the estimator that produced them, and they cannot validate the estimator that replaced it. Guard it with a test that pins the ratio meaning of a past sprint across a constants change - the label of a recorded falsification must not move when the model is refitted.

## Acceptance Criteria

### AC1: a fit-set row forecast by a retired estimator reads stale, never in-sample

- **Given** a velocity row whose retro is in `CALIBRATION_FIT_RETROS` but whose forecast was MADE by different (older, now-retired) constants
- **When** `sprint.sample_class` classifies it
- **Then** it returns `stale-constants` (it judges the estimator that made it, out-of-sample), NOT `in-sample`; a fit-set row forecast by the CURRENT constants is `in-sample`, and a non-fit row by current constants is `out-of-sample`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_bug_regressions.py::SampleClassProvenanceTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
| 2026-07-15 | sdlc-studio | Fixed: IN-SAMPLE now requires the row's forecast constants to match the current fit, so a recalibration cannot relabel the out-of-sample falsifications that justified it |
