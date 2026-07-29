# BG0414: The retro's estimate-vs-actual block is empty on a 148-point sprint: the close never runs the accuracy write it templates a home for

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; the close step, its ordering and its dry-run preview each verified by applying their own mutant)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/templates/reviews/retro.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** RETRO0083 (RUN-01KYNKDP, 47 units, 143 points claimed): the `accuracy:begin` / `accuracy:end` markers are adjacent with nothing between them. The surrounding template prose reads 'This section holds the comparison, so the question is asked every sprint instead of only when someone remembers to ask it.'
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** RUN-01KYNKDP close review; human; v1

## Summary

The retro template reserves a generated block for the estimate-versus-actual comparison and explains why it exists: so the question is asked every sprint rather than only when someone remembers. On this sprint's retro the two markers sit adjacent with nothing between them.

Nothing in the close runs `retro.py accuracy --write`. The template names the command in its own marker comment, the section prose asserts the question is asked every sprint, and the close does not ask it. The forecast data exists - `sdlc-studio/retros/evidence/forecasts-*.jsonl` is written at plan time and actuals are recorded during delivery - so the comparison is computable and simply never computed.

This is the shape of defect this run filed several of: a mechanism that exists, is documented, is templated a home, and reaches no caller. It is the same as `goal_panel` and `judge_defects_against_goal` having zero callers until this sprint wired them, and the same as `_OUTPUT_CAP` documenting a bound it did not impose.

The consequence is specific rather than cosmetic. The token-per-point rate every plan quotes is a calibration built from these rows. A 148-point sprint - the largest recorded - contributing no row means the largest available data point is missing from the series the next plan's forecast is drawn from, and nothing anywhere says it is missing. An empty block reads as 'no comparison to make', which is indistinguishable from 'the comparison was never run'.

## Steps to Reproduce

1. Open RETRO0083 and find the `accuracy:begin` marker: the next line is `accuracy:end`.
2. `grep -rn 'accuracy' .claude/skills/sdlc-studio/scripts/sprint.py` - the close does not invoke the accuracy write.
3. `sdlc-studio/retros/evidence/forecasts-2026-07-29.jsonl` exists, so the inputs were there the whole time.

## Proposed Fix

1. **The close runs it.** `sprint close` invokes the accuracy write against the run's retro, in the same step that already writes the retro's other generated content.
2. **An empty block is REFUSED, not accepted.** The close gate already checks the retro passes its content check; a retro whose accuracy block is empty on a batch that has forecasts on record should fail that check. An absence has to be distinguishable from a nil result.
3. **A genuine nil states itself.** A sprint with no forecasts on record writes 'no forecast was recorded for this batch' into the block rather than leaving it blank, so a reader can tell which of the two happened.

## Acceptance Criteria

- [ ] `sprint close` runs the accuracy write against the run's retro, so the block is populated without anyone remembering to ask.
- [ ] The close gate refuses a retro whose accuracy block is empty while forecasts exist for its batch.
- [ ] A batch with no recorded forecast writes a stated nil into the block rather than leaving it blank, so an absence is distinguishable from a nil result.
- [ ] RETRO0083's own block is populated retrospectively from the forecasts already on record, or states why it cannot be.

## Impact

The forecast is explicitly held as a hypothesis to be re-tested every sprint, and the constants are meant to move only on evidence a human has looked at. A sprint that contributes no row silently shrinks that evidence base, and the largest sprint on record contributing none skews it.

More generally: a template that reserves a home for a measurement, prose that asserts the measurement is always taken, and a close that never takes it, together produce a document that LOOKS like it reports estimate accuracy. That is worse than a retro with no such section.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | RUN-01KYNKDP close review | Filed |
