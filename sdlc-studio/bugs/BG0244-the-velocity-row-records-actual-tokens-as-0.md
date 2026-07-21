# BG0244: The velocity row records Actual (tokens) as 0 when NO unit was rated, publishing an absence as a measurement

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by dogfooding at the close of RUN-01KY2K5R, the sprint whose goal was that every published number is measured or refused. The velocity row's `Actual (tokens)` column is fed from `batch.actual_tokens`, which is the SUM over rated units. When no unit carries per-unit telemetry - the normal case for an interactive sprint - that sum is 0, and 0 is written into a column named Actual (tokens). A reader, and the estimator that reads this series, cannot distinguish 'this sprint cost zero tokens' from 'nothing was measured'. The project's own convention disagrees with the code: RETRO0062 and RETRO0063 both carry `-` in that column with a not-attributable note, because both were corrected BY HAND after the fact. RETRO0064 was corrected by hand for the third time running. That is the same argument BG0236 made for fixing rather than working around: the honest value is only recorded when somebody notices. Distinct from BG0236, which fixed the harness capture: this is the per-unit sum, a different input to the same column, and it survives that fix untouched. The `Tokens/pt` column already renders `-` correctly, so the two columns disagree with each other in the same row.

## Steps to Reproduce

1. Close an interactive sprint whose units have no per-unit telemetry records. 2. Run retro.py accuracy --id RETROxxxx --write. 3. Read the appended VELOCITY.md row. Observed: `Measured` is 0 and `Actual (tokens)` is 0, while `Tokens/pt` is `-`. Expected: `Actual (tokens)` is `-`, matching Tokens/pt and matching the hand-corrected rows for RETRO0062 and RETRO0063.

## Proposed Fix

Render `Actual (tokens)` as `-` when the rated-unit count is zero, exactly as `Tokens/pt` already does, rather than as the sum of an empty set. Zero rated units is an absence of measurement, not a measurement of zero. Carry the not-attributable reason into the row's note column so the blank is explained rather than merely blank. Guard it with a test that runs accuracy over a batch with no telemetry and asserts the column is not `0`; and add a reader-side guard so a historical `0` in that column is not consumed as a data point by the estimator - there are three such rows only because they were caught by hand, and there may be older ones nobody checked.

## Recurrence observed during the filing sprint

The hand correction DOES NOT HOLD. RETRO0064's row was corrected by hand, and `sprint close
--apply-signoff` then rewrote the velocity row from the same code path and restored the `0`. So
the workaround is not merely tedious, it is defeated by the next step of the very ceremony that
produced the wrong value: a reader who corrected the row and then completed the close would end up
publishing the false zero anyway, having done the right thing in between.

That raises the severity of the argument for fixing it. The three prior corrections (RETRO0062,
RETRO0063, RETRO0064-first-attempt) all happened to be made after the last write to the file. This
one was not, and nothing announced that the correction had been discarded.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
