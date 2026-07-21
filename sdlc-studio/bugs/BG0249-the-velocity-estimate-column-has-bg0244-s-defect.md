# BG0249: The velocity Estimate column has BG0244's defect exactly: a sum over rated units, so an unrated sprint publishes 0 as a plan-time estimate

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by the agent fixing BG0244, in the row beside the one it was fixing, and deliberately left in scope rather than swept in silently. `Estimate (tokens, plan-time)` is written from a sum over the RATED units, so an interactive sprint that rates none publishes 0 - an absence rendered as a plan-time estimate of zero tokens. It is the same falsehood BG0244 fixed in the `Actual` column of the same row, and 12 of the 17 live rows carry it today. It is arguably worse than BG0244's: an Actual of 0 is at least contradicted by the Tokens/pt cell beside it, whereas an Estimate of 0 sits next to a real forecast that WAS recorded at plan time. This sprint's own plan recorded a forecast of roughly 400,000 tokens for 16 points, so the number exists and the column simply does not read it. L-0154 applies: a defect found in one writer must be swept across every sibling writer, and this is the sibling column in the same writer.

## Steps to Reproduce

1. Close an interactive sprint, so no unit carries per-unit telemetry. 2. Read the appended VELOCITY.md row. Observed: `Estimate (tokens, plan-time)` is 0 despite the plan having recorded a real forecast at plan time. 3. Count the live rows: 12 of 17 currently carry a 0 in that column. Compare with the same row's Actual column, which BG0244 has now taught to render `-`.

## Proposed Fix

Read the plan-time forecast that was actually recorded rather than summing over rated units - the forecast log is first-record-wins precisely so this number survives, and `record_forecast` writes it unconditionally at plan time, so for most sprints the true value is on disk and simply is not being consulted. Where no forecast was recorded, render `-` as BG0244's fix now does for Actual, never 0. Apply BG0244's reader-side guard to this column too, so a historical 0 is not consumed as a data point; 12 rows are affected and none of them means zero. Guard it with a test that writes a row for a sprint with a recorded forecast and no rated units, and asserts the Estimate cell carries the forecast rather than 0 or a blank.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
