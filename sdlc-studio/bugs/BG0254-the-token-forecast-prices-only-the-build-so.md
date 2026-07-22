# BG0254: The token forecast prices only the build, so it under-forecasts by roughly an order of magnitude on a project that spends most of its budget proving the build correct

> **Status:** Fixed
> **Verification depth:** functional (the exclusion and the measured excess are asserted on the real `plan` output, over a velocity fixture carrying a plan-time forecast and a sprint actual)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-sprint.md
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Measured at RUN-01KY321Q's sign-off, the first close with a working capture. The plan forecast 400,000 tokens for 16 points at the shipped seed of 25,000 per point. The sprint delivered 18 points and cost at least 4,119,916 - over TEN TIMES the forecast. Even the published main-thread-only figure of 2,634,055 is 6.6x. Per point: 146,336 published and at least 228,884 true, against a seed of 25,000, so 5.9x and 9.2x. The seed is not slightly stale, it is describing a different activity. The reason is structural rather than a bad constant: the forecast prices the BUILD, and this project's cost is dominated by what comes after it. This sprint's four cluster agents spent 787,834 between them building all seven units, while the review, repair and re-verification rounds spent 698,027 on top of a main thread that ran to 2,634,055. A model that prices only the build will under-forecast by whatever the proving costs, and here that is most of the total. Note what this is NOT an argument for: the review caught three MAJORs this sprint including one where registering a survived mutant made the gate quieter than registering nothing, and the previous five sprints all rejected at round 1. The proving is earning its cost. The defect is that the forecast does not admit it exists, so every plan understates by design and the capacity check that reads it is calibrated against a fiction.

## Acceptance Criteria

- [x] **AC1:** The forecast declares that it prices the BUILD, and names what it excludes
      (review, repair and re-verification, orchestration, delegated spend).
      Pinned by `test_sprint.ForecastScopeTests`.
- [x] **AC2:** A whole-sprint excess is measured from velocity rows carrying both a plan-time
      forecast and a WHOLE-SPRINT actual, and printed beside the forecast. A row whose Actual
      is a per-unit build sum measures the build, not the sprint, and is excluded.
      Pinned by `test_sprint.ForecastScopeTests`.
- [x] **AC3:** With no such evidence the excess reads UNMEASURED rather than a figure, and the
      seed constant is NOT refitted.
      Pinned by `test_sprint.ForecastScopeTests`.

## Steps to Reproduce

1. Read a plan's token forecast: points x `TOKENS_PER_POINT`, currently 25,000. 2. Deliver the sprint through the normal lifecycle, including the mandatory closing review and any repair rounds. 3. Compare at sign-off. Observed for RUN-01KY321Q: forecast 400,000, published actual 2,634,055, known true actual 4,119,916 once delegated agents are counted. 4. Note that the excess is not spread across the build: the build was 787,834 of it.

## Proposed Fix

Do not simply raise the constant - that would fit a number to one sprint and would keep pricing a single undifferentiated quantity. Decide first whether the forecast should model the phases separately, because they scale differently: the build scales with points, while the review and repair scale with how much the build got wrong, which is why five consecutive round-1 rejections cost more than any of the builds did. A forecast that says '400,000 to build, and historically 1.5x to 3x that again to prove it' is useful; a single number 10x low is worse than none, because the capacity check consumes it. Prerequisites: BG0252 (the capture cannot see delegated spend, so no history is complete) and BG0248 (the measured rate cannot advance at all under interactive sprints). Both must land before any recalibration, or the new constant will be fitted to the same partial data as the old one.

## Resolution

THE CONSTANT WAS NOT TOUCHED. `POINTS_RATE_SEED` is still 25,000 and nothing was refitted -
fitting a multiplier to one measured sprint is fitting noise, and the prerequisites this bug
names (BG0252, BG0248) have not landed, so no history is complete enough to recalibrate
against. What changed is what the forecast ADMITS.

1. `FORECAST_SCOPE = "build"` and `FORECAST_EXCLUDES` name the four things the point term does
   not price: the closing review, repair rounds and the re-verification after them,
   orchestration and main-thread cost around the build, and delegated-agent spend the capture
   cannot yet see. Both ride on the forecast object and are printed with it: `this prices the
   BUILD only. It excludes: ...`.
2. `whole_sprint_excess()` is the proving term an operator can see. It reads every OUT-OF-SAMPLE
   velocity row carrying BOTH a plan-time forecast and a whole-sprint actual, and reports
   actual/forecast per sprint plus the observed span, naming the sprints. The plan prints the
   span, the sprints, and the whole-sprint figure to plan capacity against.

WHAT THAT NUMBER IS NOT, and the plan says so on its own line: it is not a measurement of
proving cost. The excess over a build forecast is proving cost PLUS whatever the build itself
was under-estimated by, and the velocity record carries no split between them. Attributing all
of it to proving would be exactly the kind of claim this batch exists to attack - a property
the figure does not have. In-sample rows are excluded, by the same rule `calibration` already
obeys, because a fit against its own training data lands near 1.0x by construction.

With no such row the plan prints `whole-sprint cost against the forecast: UNMEASURED` and
assumes no multiplier. That is the honest reading and it is pinned by its own test.

Verified functionally through `sprint.py plan`: over a fixture holding RETRO0065 (forecast
400,000, actual 2,634,055) the plan names RETRO0065 and its 6.59x, and over an empty record it
reads UNMEASURED. Five hand-applied mutants (scope renamed; repair rounds dropped from the
exclusion list; `measured` hardcoded True; the multiple inverted; the UNMEASURED wording
removed) each turned a test red and were restored.

NOT done: the forecast is still a single term multiplied by points, not a phase model. This
bug's Proposed Fix asked first for a DECISION on whether to model the phases separately; that
decision is not taken here and is not implied by this change. The capacity check still consumes
the build figure as its point estimate, with the measured whole-sprint span reported beside it.

### Repair round 1 (independent review of RUN-01KY3MFX)

Three corrections. The first two are the same defect in different places: prose claiming a
property nothing tested.

1. **The span published a BUILD figure under a whole-sprint heading.** `whole_sprint_excess`
   tested only that a forecast and an actual were both present. It never asked whether the
   Actual described the whole sprint. RETRO0028 is `Units 3 / Measured 3` - a full per-unit
   telemetry sum, which is the units' BUILD cost with the review, repair and orchestration
   around it excluded by construction - and it was published at 2.26x inside a span the plan
   labels whole-sprint. `_whole_sprint_actual` now requires the sprint-level shape the record's
   own coverage rule (`retro._tokens_cover_points`) distinguishes, and the basis line says so.
   On this repo the span is unchanged at 1.63x-6.59x; the observation count drops 4 to 3.
2. **"the plan says so on its own line" was pinned by nothing.** Deleting the caveat print left
   289 tests green - a grep for the sentence found only a test DOCSTRING. It is now asserted,
   and asserted to sit on the line immediately after the excess.
3. **The out-of-sample filter was pinned by nothing either,** and it is load-bearing: deleting
   it widened this repo's published span from 1.63x-6.59x over 4 sprints to 0.3x-6.59x over 8.
   Now asserted with a row forecast by the retired base/tpc estimator.

Four further mutants, all killed: the coverage check deleted; `_whole_sprint_actual` returning
True for every row; the caveat print deleted; the out-of-sample filter deleted.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-22 | claude-opus-4-8 | Fixed: the forecast names its scope and exclusions and carries a measured whole-sprint excess; the rate constant is unchanged |
| 2026-07-22 | claude-opus-4-8 | Repair round 1 - a per-unit build sum is no longer published as a whole-sprint excess; the caveat line and the out-of-sample filter are now pinned |
