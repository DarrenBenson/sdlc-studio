# BG1305: The Cursor meter drops the model the Cursor usage hook records on each ledger line, so a run metered from the ledger is never priced by model, and Composer pricing reaches only `sprint lane run` readings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, changelog.d/BG1305.md
> **Evidence:** `grep -c model lib/meter_cursor.py` is 0 while `cursor_usage_hook.py` names model 3 times (2026-11-09); the run nine pricing groomer's report
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T12:35:53Z

## Summary

Found grooming run nine's pricing stories on 2026-11-09. `cursor_usage_hook.py` writes `model` on each usage ledger line, but `lib/meter_cursor.py` reads the token counts and drops the model, so a reading taken from the ledger carries no model id and `lib/prices.py` reports it as not priced. Only a `sprint lane run` reading, which takes the `--model` passed to the lane, can be priced. CR0690 prices Cursor Composer in the table, but a Cursor run metered from its ledger will still read not priced, so RFC0063 outcome O11 (cost per point in money, whichever harness ran it) fails for a team on Cursor.

## Steps to Reproduce

1. Write a Cursor usage ledger line through `cursor_usage_hook.py` with a model id the price table holds.
2. Read the run's token actual through the Cursor meter in `lib/meter_cursor.py`.
3. The reading carries no model, and the sprint report prices it as not priced.

## Proposed Fix

Carry each ledger line's model through the Cursor meter into the per-model split the other meters produce, and add a test that a ledger line naming a priced model yields a dollar figure, beside a control naming an unpriced model that still reads not priced.

## Acceptance Criteria

- [ ] **AC1** Given a Cursor usage ledger whose lines name a priced model, when the Cursor meter reads it, the reading carries a per-model split in the shape the other meters produce and `lib/prices.py` prices it; beside it, a ledger line naming no model still reads as not priced. Fails on: a model-bearing ledger read as not priced, or a line with no model priced.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::LedgerCarriesTheModelTests
  - **Verified:** yes (2026-11-12)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-12 | Claude Opus 5.5 (run eleven orchestrator) | Groomed for run eleven (D0469, D0470): criteria rewritten with runnable Verify lines on the at-HEAD triage's evidence |
