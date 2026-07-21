# BG0247: The WSJF freshness advisory reports the age of scores that cover none of the batch, disguising an unused ordering as a slightly stale one

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`sprint plan --order wsjf` prints two messages that together mislead. First, honestly: 'no seat inputs (priority fallback): BG0244, BG0246, ...' - not one unit in the batch is seat-scored, so the ordering is priority and not WSJF at all. Then: 'advisory: wsjf-inputs.json is 11.3 day(s) old (window 7) - re-run the amigo consult if these scores no longer reflect current judgement'. The second message implies scores are in use and merely ageing. Inspected on 2026-07-21, the file holds 7 entries and every one is a CR from a previous era (CR0218 through CR0227), all long closed and none in any recent batch. The scores are not stale, they are IRRELEVANT, and the freshness framing hides that. The consequence is that `--order wsjf` has been silently ordering by priority for weeks while the output suggested a refresh would restore it, and an operator following the stated remedy - re-run the amigo consult - would be doing the right thing for the wrong stated reason and would have no way to tell from the message how much scoring was actually missing.

## Steps to Reproduce

1. Ensure sdlc-studio/.local/wsjf-inputs.json exists but scores only artefacts outside the current batch. 2. Run sprint.py plan --bugs Open --order wsjf. 3. Observe both the 'no seat inputs (priority fallback)' line naming every unit AND the age advisory referring to 'these scores'. Confirm by reading the file: 7 entries, all CR0218-CR0227, none in the batch.

## Proposed Fix

Report COVERAGE, not age, as the primary fact: how many units in this batch carry a seat score, out of how many. Age is only worth mentioning for scores that actually apply, so the freshness advisory should be suppressed - or explicitly reworded - when coverage is zero, because 'your scores are old' and 'you have no scores for this work' call for the same action but describe different situations, and only one of them is true. Consider making `--order wsjf` state plainly in its ordering line that it fell back, rather than leaving that to a separate message the reader must connect. Guard it with a test whose inputs file scores only out-of-batch ids and which asserts the output does not describe those scores as merely stale.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
