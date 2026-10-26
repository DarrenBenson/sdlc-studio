# BG1132: BG0962's AC7 test proves only the REJECT half of 'the frozen verdict decides' when the per-unit ledger cannot be read

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_closing_review_per_unit_verdicts.py, changelog.d/BG1132.md
> **Evidence:** BG0962 QA review, 2026-10-26, at f9f4421e: new finding 1.
> **Created:** 2026-10-26
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-26T14:26:53Z

## Summary

BG0962's QA review (APPROVE, 2026-10-26). AC7's test (test file lines 226-227) uses only a frozen REJECT, so a change that reads a `verdict_for` exception as a REJECT (`sprint_report.py`:2159-2160) passes the unit's module and three related ones (256 tests). With a frozen APPROVE and `verdict_for` raising, the shipped code reads 'ran 1 unit(s) approved' and the mutant reads 'not-run 1 unresolved'. The gap can only hold a unit back, never clear one.

## Steps to Reproduce

Change the except branch to treat a raising `verdict_for` as a REJECT; run the module: green.

## Proposed Fix

Add a frozen-APPROVE case to AC7's test asserting the checklist reads `ran`.

## Acceptance Criteria

- [ ] **AC1** Given a frozen APPROVE and a per-unit ledger whose read raises, then the closing-review row reads ran
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_closing_review_per_unit_verdicts.py::ClosingReviewPerUnitTests::test_an_unreadable_per_unit_ledger_leaves_a_frozen_approve_standing

## Impact

A regression that holds every unit whose per-unit ledger is unreadable would pass.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-26 | Claude Opus 5.5 | Filed |
