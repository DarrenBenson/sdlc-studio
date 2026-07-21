# BG0244: The velocity row records Actual (tokens) as 0 when NO unit was rated, publishing an absence as a measurement

> **Status:** Fixed
> **Verification depth:** functional - the false zero was reproduced through the writer that produces it (an interactive sprint with no telemetry: `Actual (tokens)` came out `0` beside a `Tokens/pt` of `-`), then fixed, then the fix was mutation-proven with 8 hand-applied mutants, all killed. The reader guard was checked against the LIVE VELOCITY.md by running `retro.py velocity` read-only under the pre-fix and post-fix code: 7 historical rows moved from `actual= 0` to `actual= -`, 4 rows stopped publishing a `0/pt` rate (RETRO0058 and the 3 hand-corrected ones), and the 3 hand-corrected rows stopped reporting their reason prose as the delivering MODEL.
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by dogfooding at the close of RUN-01KY2K5R, the sprint whose goal was that every published number is measured or refused. The velocity row's `Actual (tokens)` column is fed from `batch.actual_tokens`, which is the SUM over rated units. When no unit carries per-unit telemetry - the normal case for an interactive sprint - that sum is 0, and 0 is written into a column named Actual (tokens). A reader, and the estimator that reads this series, cannot distinguish 'this sprint cost zero tokens' from 'nothing was measured'. The project's own convention disagrees with the code: RETRO0062 and RETRO0063 both carry `-` in that column with a not-attributable note, because both were corrected BY HAND after the fact. RETRO0064 was corrected by hand for the third time running. That is the same argument BG0236 made for fixing rather than working around: the honest value is only recorded when somebody notices. Distinct from BG0236, which fixed the harness capture: this is the per-unit sum, a different input to the same column, and it survives that fix untouched. The `Tokens/pt` column already renders `-` correctly, so the two columns disagree with each other in the same row.

## Acceptance Criteria

- [x] **AC1:** A sprint that rates no unit publishes `-` in Actual (tokens), never `0`, so an absence is never rendered as a measurement of zero.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_retro.py
- [x] **AC2:** The row carries a Note giving the not-attributable reason, so the blank is explained rather than merely blank.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_retro.py
- [x] **AC3:** A historical `0` already in the file is treated as absent by every reader, so the three hand-corrected rows cannot be consumed as data points and the correction survives a whole-file rewrite.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_retro.py

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

## Resolution

Four changes in `retro.py`, three of them where the filed proposal asked and one the
investigation added.

1. **The writer.** `record_velocity` clears a falsy `actual_tokens` to `None` after the
   existing preservation and retraction rules have had their say, so the cell renders `-`. The
   `--tokens 0` retraction (BG0224) and the reuse of an already-recorded actual both still
   behave as they did; only the empty rated-unit sum changes.
2. **The reason.** A `Note` column was added to the history. The three hand corrections had
   nowhere to write their reason but the last cell, which is the Model column - so the file
   was already telling us the column was missing. `_actual_note` prefers the close's own
   not-attributable reason (it names the run, the meter or the missing baseline) and falls
   back to a generic statement of the same fact for a plain re-run.
3. **The reader.** `velocity_history` reads a recorded `0` in that column as ABSENT. No sprint
   costs zero tokens, so a `0` there can only be the old writer's empty-set sum; read as a
   number it is a data point about what a sprint cost. The same read salvages a Model cell
   holding prose (a hand correction) into the note, so a sentence never reaches the per-model
   segmentation as a model. The next whole-file rewrite then republishes both correctly, which
   is what makes this self-healing rather than another correction waiting to be overwritten.
4. **A second consumer, found while proving point 3.** `retro.py velocity` divided the Actual
   cell by the points unconditionally and printed `0/pt` on the same line as `actual= -`. On
   the live history that was 4 rows. It now obeys the rule the file's own `Tokens/pt` column
   obeys (`_tokens_cover_points`).

Not fixed, and NOT claimed to be: the `Estimate` column has the identical shape (a sum over the
rated units, so `0` for a sprint that rated none) and 12 of the 17 live rows carry that `0`. It
is outside this bug's scope, it is the same class of falsehood, and it is worth its own bug.

### Repair round 1: the review found the fix reproducing the defect inside the new column

The independent review REJECTed the sprint on two findings in the work above, both in
`_actual_note`/`record_velocity`.

**The `Note` was destroyed by the next write of its OWN row.** Point 1 preserved a previously
recorded `actual_tokens` across a re-run; the note beside it was regenerated unconditionally,
so a recorded reason - and any number it carried - was replaced by the generic sentence. AC3
claimed the correction "survives a whole-file rewrite", which held only for rewrites triggered
by OTHER rows. Every note test wrote the note on one row and then recorded a different one, so
the same-row case was never exercised. Reproduced against a copy of the live history:
`accuracy --id RETRO0063 --write` replaced `raw capture 5,672,289` - a figure recorded nowhere
else in the project - with the generic sentence. `_actual_note` now takes the reason already
recorded against the row and returns it when this run has nothing more specific to say. A cell
that has since been FILLED still drops its reason: a reason explains a blank.

**An explicit `--tokens 0` published a false reason.** The retraction path is the one case
`record_velocity` reasons about by name (`sprint_tokens_supplied`), and `_actual_note` fell
through it into a sentence asserting "no sprint total was supplied". A total was supplied,
deliberately, as zero, to withdraw a wrong figure - and to a human the generic sentence reads
as nobody having looked yet. The retraction now writes its own reason, and it outranks a
preserved one, because it is this run's own statement about the cell.

Order in `_actual_note` is now: this run's own statement (the close's not-attributable reason,
then a retraction), then the reason already on the row, then the generic fact.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | claude | Fixed: writer clears the empty-set sum, `Note` column carries the reason, reader treats a historical `0` as absent and salvages prose out of the Model cell, and `retro.py velocity` stopped deriving `0/pt` from an absent actual. 8 mutants applied by hand, 8 killed. |
| 2026-07-21 | claude | Review REJECT, repair round 1. Two MAJORs, both reproducing this bug inside its own fix: a recorded `Note` was overwritten by the re-record of its own row (RETRO0063's `raw capture 5,672,289` destroyed, proven against a copy and now proven to survive), and `--tokens 0` published "no sprint total was supplied" about the one case where one deliberately was. Same-row re-record now has a test; 4 mutants applied by hand across the two branches, 4 killed. |
