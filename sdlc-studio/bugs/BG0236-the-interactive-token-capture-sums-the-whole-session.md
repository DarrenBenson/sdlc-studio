# BG0236: the interactive token capture sums the whole session, so a second sprint in one session double-counts the first sprint's tokens

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py,.claude/skills/sdlc-studio/scripts/lib/run_state.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

accuracy --tokens-from-harness reads the current sessions entire transcript usage. When two sprints are closed in ONE session - RUN-01KY03GS then RUN-01KY0VNV here - the second close captures the whole session total, which already includes every token the first sprint (and its close, and an incident recovery) spent. RETRO0061 recorded 1,265,392 tokens; RETRO0062, three small bug fixes forecast at ~200,000, recorded 2,731,602 - a figure that is mostly the first sprint and the conversation overhead, not this sprints delivery. It wrote 341,450 tokens/point into VELOCITY.md, ~13x the measured ~25,000/pt rate, as if it were a measurement. This is the token-axis twin of BG0218: a number that reads as a per-sprint cost but is actually a per-session cumulative, and it silently corrupts the tokens/point series the moment more than one sprint shares a session.

RECURRED at the close of RUN-01KY1WCR, the THIRD sprint in the same session: the capture returned 5,672,289 and wrote 472,691 tokens/point over 12 points, ~19x the measured rate. The error grows with session length, so it is worst exactly where a long adversarial review makes the real cost most interesting. Blanked as not-attributable in VELOCITY.md again, by hand again. Two consecutive closes have now had to be manually corrected after the fact, which is the argument for the fix rather than the workaround: the honest value is only recorded when someone notices, and the failure mode is a published number that looks measured.

## Steps to Reproduce

Close two sprints in one interactive session. The first records a plausible token total; the second records the cumulative session total (first sprint + close + everything since), divided by only the second sprints points. Observed: RETRO0062 row shows 2,731,602 tokens / 8 points = 341,450/pt against a ~25,000/pt measured rate and a ~200,000 forecast for the batch.

## Proposed Fix

The capture must attribute only the tokens spent SINCE the run opened, not the whole session. Record a session-token baseline on the run state at sprint plan --write (`open_run)`, and at close capture the delta from that baseline rather than the absolute total. A run whose baseline is missing (opened before this fix) reports the token total as not-attributable rather than as a measurement, the same way an unmeasured elapsed is handled. Guard it with a test that opens two runs in one session and asserts the second captures only its own delta.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | sdlc-studio | Recurrence recorded: RUN-01KY1WCR close captured 5,672,289 (472,691/pt) as the third sprint in one session |
