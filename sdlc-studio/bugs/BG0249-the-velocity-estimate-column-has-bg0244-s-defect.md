# BG0249: The velocity Estimate column has BG0244's defect exactly: a sum over rated units, so an unrated sprint publishes 0 as a plan-time estimate

> **Status:** Fixed
> **Verification depth:** functional - the false zero was reproduced through the writer that
> produces it (a batch forecast at plan time with no unit measured published `0` in a column
> named `Estimate (tokens, plan-time)`), then fixed red-to-green, then mutation-proven with 5
> hand-applied mutants, all killed. Checked against the LIVE record: reading the pre-fix file
> back, 12 rows carried a `0` estimate; after the fix all 12 read as absent, and the 13 whose
> plan-time forecast is still on disk now publish it (RETRO0044 750,000 through RETRO0065
> 400,000). `measured_rate` returns the same figures before and after, so no rate moved.
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

## Acceptance Criteria

- [x] **AC1:** A sprint with a recorded plan-time forecast and no rated unit publishes that
      forecast in the Estimate column, not `0` and not a blank.
      Pinned by `test_retro.TheEstimateColumnIsTheForecastThatWasRecorded`.
- [x] **AC2:** A sprint that recorded no forecast publishes `-`, because 0 is a prediction
      nobody made.
      Pinned by `test_retro.TheEstimateColumnIsTheForecastThatWasRecorded`.
- [x] **AC3:** A historical `0` already in the file is read as absent and is not republished as
      a number, so it cannot be consumed as a data point.
      Pinned by `test_retro.TheEstimateColumnIsTheForecastThatWasRecorded`.
- [x] **AC4:** The ratio still judges only the rated units, so widening the published estimate
      does not widen the numerator it is divided by.
      Pinned by `test_retro.test_the_ratio_still_judges_only_the_rated_units`.

## Resolution

Four changes in `retro.py`, following BG0244's shape rather than inventing a second idiom.

1. **The producer.** `accuracy` gains `batch.plan_estimate`: the forecast summed over every
   unit that HAS one, not over the rated units. `batch.estimate` is untouched and stays the
   ratio's numerator, which must describe exactly the units `actual_tokens` describes. The two
   sums answer different questions and are now two values rather than one doing both jobs
   badly.
2. **The writer.** `record_velocity` writes the Estimate cell from `plan_estimate`, and a falsy
   value is an absence that renders `-`.
3. **The reader.** `velocity_history` reads a recorded `0` estimate as absent, exactly as
   BG0244 taught it to read the Actual cell beside it. The next whole-file rewrite republishes
   it as `-`, so the correction is self-healing rather than another hand fix awaiting an
   overwrite.
4. **Preservation.** A recorded estimate survives a re-record that can no longer see the
   forecast. The forecast log lives in `.local/`, which is not committed, so a re-run on
   another clone reads none; L-0156 says a rewrite must never replace a recorded number with
   the absence of one.

On the live record: the 12 zeros are gone, and the 13 rows whose plan-time forecast is still in
the forecast log now publish it. That was done by writing the Estimate cell ALONE on the rows
that already existed, not by re-recording the row: RETRO0044's row records 13 units where
today's batch line parses 8, and a whole-row rewrite would have replaced a recorded fact with
today's re-derivation, which is what the file's own header forbids. The forecasts themselves are
read from the plan-time log, never re-derived from the constants in force.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-22 | sdlc-studio | Fixed: plan_estimate replaces the rated-unit sum; reader, writer and live record corrected |
