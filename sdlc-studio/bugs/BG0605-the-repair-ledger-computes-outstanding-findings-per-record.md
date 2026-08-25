# BG0605: The repair ledger computes outstanding findings per RECORD, so two partial repairs that together close everything both read as PARTIAL

> **Status:** Fixed
> **Severity:** Medium
> **Verification depth:** functional [[derived: criteria 2; plan rows 2; executed 2; killed 2; survived 0; not-run 0; entry point 0 of 2 criteria through the shipped CLI, 2 in-process | fp ae72f7a3576b ]] (a repair split across two invocations and a genuinely partial one, so the roll-up is shown to discriminate rather than to report `complete` for any repair at all)
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01M0JD1W close, 2026-08-24. Four units, eight repair records, every finding closed across the pairs, and all eight rows read PARTIAL with a false residue.
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`critic.py repair` computes the outstanding set from the closures in THAT invocation alone, not from every repair record the unit already carries. A unit whose REJECT raised three findings and whose repairs were recorded in two calls - one closing #1, a second closing #2 and #3 - ends with two rows in repair-record.md, each stamped PARTIAL, each naming as outstanding the findings the OTHER row closed. Nothing in the ledger says the unit is fully repaired, though it is.

## Steps to Reproduce

1. Record a REJECT raising three findings on a unit. 2. Run `critic.py repair --unit <id> --closed '#1 -> evidence'`. 3. Run `critic.py repair --unit <id> --closed '#2 -> evidence; #3 -> evidence'`. 4. Read sdlc-studio/reviews/repair-record.md: both rows say PARTIAL, and the outstanding column of each names findings the other row closed. Observed on RUN-01M0JD1W, 2026-08-24, closing US0671, US0672, US0673 and US0675.

## Proposed Fix

Compute the outstanding set as the verdict's findings MINUS the union of closures across every repair record for that unit and phase, rather than minus this invocation's closures. Report the row's own contribution separately from the unit's residue, so a partial record stays honest about what IT closed while the unit's status reflects the whole ledger.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose REJECT raised two findings and whose closures were recorded across TWO `repair` invocations covering both, when the repair state is read, then it reads COMPLETE - not two rows each stamped PARTIAL, each naming as outstanding what the other closed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_a_repair_recorded_across_two_calls_reads_complete
- [ ] **AC2** Given a unit whose repair closes a strict SUBSET of its findings, when the state is read, then it still reads PARTIAL - the paired control, because reading every row must not turn an unanswered finding into an answered one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_a_genuinely_partial_repair_still_reads_partial

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `critic.py`, narrow `repair_state`'s closures to the latest repair row | Given a unit whose REJECT raised two findings and whose closures were recorded across TWO `repair` invocations covering both, when the repair state is read, then it reads COMPLETE - not two rows each stamped PARTIAL, each naming as outstanding what the other closed |
| AC2 | in `critic.py`, replace `repair_state`'s outstanding check with an unconditional `complete` | Given a unit whose repair closes a strict SUBSET of its findings, when the state is read, then it still reads PARTIAL - the paired control, because reading every row must not turn an unanswered finding into an answered one |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
