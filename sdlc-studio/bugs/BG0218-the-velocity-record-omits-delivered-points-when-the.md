# BG0218: the velocity record omits delivered points when the units carry no plan-time forecast

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional (a sprint of unforecast-but-sized units records its point total in the velocity row while ratio and estimate stay gated - the exact scenario from the report, plus the new guard proven both ways: a partially measured sprint contributes points to the series but is excluded from the derived rate, and every fully measured fixture keeps its rate; backfilled live on RETRO0058, whose row now records the 14 points it delivered)
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

VELOCITY.md's Points column reads '-' for a sprint that delivered 14 points across 6 sized units. The points are known: every unit carries a Points field, and the retro states the total. They are dropped because the accuracy table only counts units that had a plan-time forecast, and a unit built before its run was opened has none, so it is excluded from BOTH sides and its points vanish with it. RETRO0057 and RETRO0058 both record Points '-' this way. A velocity record that cannot state points delivered is not a velocity record - points-per-sprint is the primary series it exists to hold, and it is independent of whether anyone forecast the unit. Distinct from CR0284, which covers the tokens-per-point rate and the enforcement gap; this is the points series itself going unrecorded even when accuracy IS run.

## Steps to Reproduce

1. Deliver sized units without a plan-time forecast (build first, open the run after - the common interactive case). 2. Run retro.py accuracy --id RETROxxxx --write. 3. The per-unit rows show Points '-' for the unforecast units although their artefacts carry Points. 4. VELOCITY.md's row for the sprint records Points '-' rather than the delivered total.

## Proposed Fix

Record delivered points from the units' own Points fields, independently of whether a forecast existed. Keep the forecast-gated exclusion for the RATIO columns, where it is correct - an unforecast unit really does say nothing about estimator accuracy - but the points series must not inherit that exclusion. Add a test asserting a sprint of unforecast-but-sized units still records its point total.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
