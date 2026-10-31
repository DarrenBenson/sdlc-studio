# BG1136: BG0962's AC7 test pins only the frozen-REJECT half of 'an unreadable per-unit ledger is read as no verdict'

> **Status:** Superseded
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_unreadable_ledger_frozen_approve.py
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-31T19:41:48Z

## Summary

**Duplicate of BG1132**, which BG0962's round-three QA review filed on 2026-10-26 for the same half-pinned AC7 test. Closed as Superseded on 2026-10-31; BG1132's repair must also kill the round-2 review's mutant X14 (the except branch writing a per-unit REJECT).

`test_an_unreadable_per_unit_ledger_does_not_break_the_checklist` makes `verdict_for` raise only under a frozen REJECT, where no per-unit verdict and a per-unit REJECT give the same answer. A mutant in which the except branch in `sprint_report.py`'s closing-review fold also writes a per-unit REJECT passes the unit's tests and `test_sprint_report.py`; under it a frozen APPROVE with `verdict_for` raising reads not-run, 1 unresolved, where HEAD reads ran. It fails closed. Found by BG0962's round-2 QA review on 2026-10-28.

## Steps to Reproduce

In a throwaway copy, make the except branch after `verdict_for` in the closing-review fold record a REJECT for the unit, then run the unit's test module and `test_sprint_report.py`: all pass.

## Proposed Fix

Add a frozen-APPROVE subcase under the same patch that asserts the item reads RAN, as BG0441 AC3 does for `review_coverage` in `test_lean_one_verdict_ledger.py.`

## Acceptance Criteria

- [ ] **AC1** With `verdict_for` raising and a frozen APPROVE, the closing-review item reads RAN, and the test fails if the except branch writes a per-unit REJECT.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_unreadable_ledger_frozen_approve.py

## Impact

The sentence 'the frozen verdict decides' and the comment that `verdict_for` raising leaves no per-unit verdict are pinned only against the raise escaping.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Filed |
