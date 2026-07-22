# BG0247: The WSJF freshness advisory reports the age of scores that cover none of the batch, disguising an unused ordering as a slightly stale one

> **Status:** Fixed
> **Verification depth:** functional (an inputs file scoring only out-of-batch ids drives the real `plan --order wsjf` path; the output is asserted to carry no age advisory)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`sprint plan --order wsjf` prints two messages that together mislead. First, honestly: 'no seat inputs (priority fallback): BG0244, BG0246, ...' - not one unit in the batch is seat-scored, so the ordering is priority and not WSJF at all. Then: 'advisory: wsjf-inputs.json is 11.3 day(s) old (window 7) - re-run the amigo consult if these scores no longer reflect current judgement'. The second message implies scores are in use and merely ageing. Inspected on 2026-07-21, the file holds 7 entries and every one is a CR from a previous era (CR0218 through CR0227), all long closed and none in any recent batch. The scores are not stale, they are IRRELEVANT, and the freshness framing hides that. The consequence is that `--order wsjf` has been silently ordering by priority for weeks while the output suggested a refresh would restore it, and an operator following the stated remedy - re-run the amigo consult - would be doing the right thing for the wrong stated reason and would have no way to tell from the message how much scoring was actually missing.

## Acceptance Criteria

- [x] **AC1:** With no seat score covering the batch, the plan reports COVERAGE and prints no
      staleness advisory, because an age is only meaningful about scores that are in use.
      Pinned by `test_sprint.SeatCoverageTests`.
- [x] **AC2:** A scores file whose every entry is about out-of-batch work is named as covering
      none of this batch, rather than described as merely ageing.
      Pinned by `test_sprint.SeatCoverageTests`.
- [x] **AC3:** The `priority fallback` wording is corrected: Cost of Delay derived from Priority
      is still WSJF, so the line no longer implies the ordering was abandoned.
      Pinned by `test_sprint.SeatCoverageTests`.

## Steps to Reproduce

1. Ensure sdlc-studio/.local/wsjf-inputs.json exists but scores only artefacts outside the current batch. 2. Run sprint.py plan --bugs Open --order wsjf. 3. Observe both the 'no seat inputs (priority fallback)' line naming every unit AND the age advisory referring to 'these scores'. Confirm by reading the file: 7 entries, all CR0218-CR0227, none in the batch.

## Proposed Fix

Report COVERAGE, not age, as the primary fact: how many units in this batch carry a seat score, out of how many. Age is only worth mentioning for scores that actually apply, so the freshness advisory should be suppressed - or explicitly reworded - when coverage is zero, because 'your scores are old' and 'you have no scores for this work' call for the same action but describe different situations, and only one of them is true. Consider making `--order wsjf` state plainly in its ordering line that it fell back, rather than leaving that to a separate message the reader must connect. Guard it with a test whose inputs file scores only out-of-batch ids and which asserts the output does not describe those scores as merely stale.

## Resolution

What the code now does, and only that.

`_seat_provenance` carries `entries` (how many ids the file scores), `covered` (how many of
them are in this batch) and `irrelevant` (the file scores something, but nothing here). `stale`
gained one condition: it is true only when scores that ACTUALLY APPLY are past the window. A
thing with no bearing on this batch cannot go off, so an inputs file covering none of the batch
now reports `stale: false` and `irrelevant: true`.

`_render_seat_provenance` leads with coverage - `seats: 0/2 unit(s) in this batch carry a seat
score (7 entries in wsjf-inputs.json)` - and, when coverage is zero, prints that the file scores
no unit in this batch and that its entries are about other work, INSTEAD of the age advisory.
The advisory survives unchanged for the case it was written for: scores that do apply and are
past the window still print their age.

A CORRECTION to this bug's own text, recorded rather than quietly implemented. The Summary says
"not one unit in the batch is seat-scored, so the ordering is priority and not WSJF at all".
That is FALSE under the current design and it was false when filed: `_order_batch` derives the
Cost of Delay from the declared Priority when no seat score exists, and still ranks by
CoD/Points. Only the CoD falls back; the ordering is still WSJF. The old message
(`no seat inputs (priority fallback)`) is what made the bug's author believe otherwise, and it
is the same defect class as the age advisory - a message describing a situation other than the
one on screen. It now reads `Cost of Delay derived from Priority for: ... - the order is still
WSJF (CoD/Points), only the CoD is derived`, and a test asserts the batch really does carry a
`wsjf` score and a `cod_source` of `priority` while that line prints.

Verified functionally through `sprint.py plan --order wsjf` (not by calling the helper): with a
file scoring only `CR0900` and dated 11 days old over a batch of `CR0001`/`CR0002`, the output
contains no `day(s) old` line and does contain `0/2`. Three hand-applied mutants (drop the
coverage guard on `stale`; hardcode `irrelevant` False; restore the old fallback wording) each
turned the tests red and were restored.

NOT done, and not claimed: nothing re-scores anything, nothing refuses a plan over zero
coverage, and the seat consult itself is untouched - this bug is about what the plan SAYS.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-22 | claude-opus-4-8 | Fixed: coverage leads, the age advisory is suppressed at zero coverage, and the fallback line no longer claims the order fell back to priority |
