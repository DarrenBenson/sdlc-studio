# BG0367: The AC-less baseline is not one-way, so a newly filed unit can be added to it and exempt itself

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0515 baselines the units that already reach terminal with no acceptance criteria so US0514's refusal does not block the existing corpus. The baseline is read as a plain set with no rule that it may only shrink, so adding an id to it is a supported way to bypass the criteria floor entirely - the exemption the baseline exists to time-box becomes permanent and extensible.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review. Nothing in the check compares the baseline against its previous contents or against the unit's creation date, so an id created after the baseline was taken is honoured identically to one created before it.

## Proposed Fix

Make the baseline one-way: a unit created after the baseline was taken is never exempt regardless of membership, and a guard reports when the baseline grows. Record the baseline date in the file so the rule has something to compare against.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: none of its prose fields carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
