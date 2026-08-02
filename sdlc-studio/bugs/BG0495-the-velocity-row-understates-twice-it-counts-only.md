# BG0495: the velocity row understates twice - it counts only accepted points, over a wall-clock with no idle deducted

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/loop_guard.py, sdlc-studio/retros/VELOCITY.md
> **Severity:** Medium
> **Points:** 3

## Summary

RETRO0089 recorded 4.96 points/elapsed-hour for RUN-01KYZKY5 and the operator immediately queried it: the sprint was planned at 152 points and ran about 15 hours. Both halves of the ratio are wrong, and both in the same direction.

NUMERATOR. The row counts 76 points, being the units in a TERMINAL status. The batch holds 148 points; 72 of those are delivered, committed, working code sitting at Ready because the review rejected it. So the figure measures ACCEPTED work while its label says only 'points', and a run that wrote 148 points and had 72 rejected is reported as a run that was slow rather than one that was rejected. Those are different facts and only one of them is a velocity.

DENOMINATOR. `sprint stop` reported '15.312h wall-clock less 0.0h idle INSIDE it, from 0 recorded gap(s)'. This was an interactive session containing six full suite runs of roughly nine minutes each and several long periods with nobody at the keyboard. Zero recorded idle across fifteen hours is not credible, so the elapsed figure is closer to a calendar span than to working time.

Combined, the two push the ratio far below the operator's own felt heuristic of roughly three minutes per point, which is what made it visible.

## Steps to Reproduce

1. Read the Velocity line in RETRO0089: 4.96 points/elapsed-hour, 76 points over 15.312h.
2. Sum the batch's points by terminal status: 76 terminal across 25 units, 72 non-terminal across 19, 148 total.
3. Read the `sprint stop` output: 0.0h idle from 0 recorded gaps, over a 15.3h interactive run.

## Proposed Fix

Report the two numerators separately and label them: points DELIVERED (written, committed, gate-green) and points ACCEPTED (terminal after review). A run that delivers 148 and has 72 rejected should show both, since the gap is the most interesting number on the row. For the denominator, either record idle gaps for an interactive run or state plainly that the elapsed figure is a calendar span with no idle deduction - an unqualified 'working hours' that is really wall-clock is a claim the tooling cannot support.

## Impact

VELOCITY.md is what the plans quote, and the estimator memo already warns that velocity is descriptive and never a target. A number that understates by roughly half on the numerator and an unknown amount on the denominator does not just mislead about speed - it hides the actual finding, which is that a fifth of this batch was rejected on review. The first person to act on it would conclude the team is slow rather than that the evidence was weak.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
