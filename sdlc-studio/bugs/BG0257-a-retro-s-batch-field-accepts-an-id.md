# BG0257: A retro's Batch field accepts an id RANGE, silently reads 4 units instead of 33, and publishes a velocity row an order of magnitude wrong

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py,.claude/skills/sdlc-studio/scripts/templates/retro.md
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Hit live at RUN-01KY3MFX's close. The retro's Batch line was written as 'BG0247-BG0256, US0288-US0310 (32 units, 100 points)' - a range, which reads naturally and is what a human would write. The parser expands no ranges, so it matched only the four bare ids it could see and `accuracy --write` published 'Sprint tokens/point: 2,597,269 (5,194,538 tokens over 2 delivered points)'. That number is wrong by roughly three orders of magnitude and it went into VELOCITY.md, which the header describes as the source the planner re-measures its rate from. It was caught by reading the output, not by any check. The failure is silent and fails open in the worst direction for this project: a plausible-looking number in the one file whose entire purpose is to be trusted later. Note the shape - the field is prose that the tooling parses, so a writer gets no feedback that half their batch was ignored, and the count is not cross-checked against anything. The retro's own header states the unit count separately (it said 32, and the batch names 33), so the data to detect this was present and unused.

## Steps to Reproduce

1. Write a retro whose Batch field expresses ids as a range, for example 'BG0247-BG0256, US0288-US0310'. 2. Run retro.py accuracy --id <retro> --tokens N --write. Observed: the accuracy table lists only the bare ids the parser recognised, the points denominator is the sum of those alone, and a tokens-per-point figure computed from the full token numerator over that partial denominator is written to VELOCITY.md. Expected: either the range is expanded, or the mismatch between the parsed unit count and the retro's declared unit count is refused.

## Proposed Fix

Cross-check the parsed batch against the retro's own declared unit count and REFUSE when they disagree, rather than expanding ranges - expansion invites a second ambiguity about what a range across two id families means. The count is already written in the header, so the check costs nothing. Whatever is chosen, a partially-parsed batch must never reach `record_velocity`: a wrong row in the file the planner re-measures from is worse than no row.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
