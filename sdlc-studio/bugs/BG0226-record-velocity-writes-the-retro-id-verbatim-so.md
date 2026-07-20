# BG0226: record_velocity writes the retro id verbatim, so a dashed id mints a row the history reader cannot see

> **Status:** Open
> **Severity:** Medium
> **Verification depth:** functional (reader and writer fixed and independently covered; reverting the writer alone initially still passed because the tolerant reader masked it - the incidental-pass trap - so an on-disk line assertion was added and the writer mutant then failed)
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`record_velocity` stamps the row with res id upper-cased verbatim; a close whose retro id came from the scaffold in dashed form (RETRO-0060) therefore writes a row `velocity_history`'s strict id regex never parses. Every consumer is blind to it: the points series loses the sprint, `measured_rate` cannot use it, and the tokens-from-harness reuse guard finds no recorded actual and re-captures on every tail re-run - observed live at the RUN-01KXZQF0 close, where the second apply-signoff re-read the transcript (2,379,398 then 2,390,624) instead of reusing. Self-healing by accident: the next visible write rebuilds the file from parsed history and drops the invisible row. Same class as the retro-id-resolves-either-form lesson.

## Steps to Reproduce

1. Scaffold a retro via sprint close (id prints dashed, e.g. RETRO-0060). 2. Run close --apply-signoff so the tail records the velocity row with that id. 3. `velocity_history()` omits the row; a second tail run re-captures the token actual instead of reusing it.

## Proposed Fix

Normalise the id in `record_velocity` (strip the dash before writing, as the retro-id resolver already does elsewhere), and add a test that a dashed-id accuracy write produces a row `velocity_history` parses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
