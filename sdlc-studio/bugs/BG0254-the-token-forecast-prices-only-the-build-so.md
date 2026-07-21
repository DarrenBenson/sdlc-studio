# BG0254: The token forecast prices only the build, so it under-forecasts by roughly an order of magnitude on a project that spends most of its budget proving the build correct

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-sprint.md
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Measured at RUN-01KY321Q's sign-off, the first close with a working capture. The plan forecast 400,000 tokens for 16 points at the shipped seed of 25,000 per point. The sprint delivered 18 points and cost at least 4,119,916 - over TEN TIMES the forecast. Even the published main-thread-only figure of 2,634,055 is 6.6x. Per point: 146,336 published and at least 228,884 true, against a seed of 25,000, so 5.9x and 9.2x. The seed is not slightly stale, it is describing a different activity. The reason is structural rather than a bad constant: the forecast prices the BUILD, and this project's cost is dominated by what comes after it. This sprint's four cluster agents spent 787,834 between them building all seven units, while the review, repair and re-verification rounds spent 698,027 on top of a main thread that ran to 2,634,055. A model that prices only the build will under-forecast by whatever the proving costs, and here that is most of the total. Note what this is NOT an argument for: the review caught three MAJORs this sprint including one where registering a survived mutant made the gate quieter than registering nothing, and the previous five sprints all rejected at round 1. The proving is earning its cost. The defect is that the forecast does not admit it exists, so every plan understates by design and the capacity check that reads it is calibrated against a fiction.

## Steps to Reproduce

1. Read a plan's token forecast: points x `TOKENS_PER_POINT`, currently 25,000. 2. Deliver the sprint through the normal lifecycle, including the mandatory closing review and any repair rounds. 3. Compare at sign-off. Observed for RUN-01KY321Q: forecast 400,000, published actual 2,634,055, known true actual 4,119,916 once delegated agents are counted. 4. Note that the excess is not spread across the build: the build was 787,834 of it.

## Proposed Fix

Do not simply raise the constant - that would fit a number to one sprint and would keep pricing a single undifferentiated quantity. Decide first whether the forecast should model the phases separately, because they scale differently: the build scales with points, while the review and repair scale with how much the build got wrong, which is why five consecutive round-1 rejections cost more than any of the builds did. A forecast that says '400,000 to build, and historically 1.5x to 3x that again to prove it' is useful; a single number 10x low is worse than none, because the capacity check consumes it. Prerequisites: BG0252 (the capture cannot see delegated spend, so no history is complete) and BG0248 (the measured rate cannot advance at all under interactive sprints). Both must land before any recalibration, or the new constant will be fitted to the same partial data as the old one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
