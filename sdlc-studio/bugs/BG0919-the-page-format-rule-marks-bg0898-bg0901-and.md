# BG0919: The page-format rule marks BG0898, BG0901 and BG0904 added have no file-then-revalidate pin

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_rule_marks_round_trip.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T00:26:01Z

## Summary

Each of BG0898, BG0901 and BG0904 added an envelope rule mark so pages filed before it re-derive as signed. Nothing files a page under the new rule and revalidates it: the BG0901 reviewer dropped `AGENT_MINUTES_RULE`'s mark (`sprint_report.py` ~4173) or hard-wired revalidate (~5219) and 311 tests passed while such a page re-derived INVALID. BG0900's repair pins its own mark (D0320).

## Steps to Reproduce

1. Drop one of the three rule marks from the envelope. 2. File a page whose figures the new rule changes, then revalidate it. 3. It reads INVALIDATED and no test fails.

## Proposed Fix

One parametrised test that files a page under each new rule and revalidates it VALID, and INVALIDATED with the mark dropped. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a page filed under each of the minutes like-for-like, partial agent minutes and cancelled-run DORA rules, when it is revalidated, then it reads VALID, and with that rule's envelope mark dropped it reads INVALIDATED. Fails on: a mutant dropping any one mark, which the current suite does not kill
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_rule_marks_round_trip.py::RuleMarksRoundTripTests::test_each_rule_mark_round_trips
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
