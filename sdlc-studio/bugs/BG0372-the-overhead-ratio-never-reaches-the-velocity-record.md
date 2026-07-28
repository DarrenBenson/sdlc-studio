# BG0372: The overhead ratio never reaches the velocity record, so the measurement is taken and discarded

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0523 and US0524 compute a delivery-against-overhead ratio and report it at the close. Nothing writes it to retros/VELOCITY.md, which is the only place a figure survives to be compared across sprints, so the instrument answers the question once per sprint and forgets. The measurement exists to show a trend and the trend cannot be assembled.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review by following the ratio from computation to output: it reaches the close report and stops. The velocity row written by the accuracy path carries points and tokens and no overhead term.

## Proposed Fix

Add the ratio and its unattributed remainder to the velocity row written at close, so successive sprints are comparable, and report it as unmeasured in the row when the run could not attribute it.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: none of its prose fields carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
