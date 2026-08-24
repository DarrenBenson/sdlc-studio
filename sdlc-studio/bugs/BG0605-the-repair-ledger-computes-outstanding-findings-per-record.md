# BG0605: The repair ledger computes outstanding findings per RECORD, so two partial repairs that together close everything both read as PARTIAL

> **Status:** Open
> **Severity:** Medium
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

- [ ] **AC1** Given a unit whose REJECT raised three findings and whose closures were recorded across two `repair` invocations covering all three, when the second is recorded, then the unit's residue is reported as empty rather than as the findings the first invocation closed
- [ ] **AC2** Given a unit with one repair record closing a strict subset of its findings, when that record is read, then the findings it did not close are still reported as outstanding for the unit
- [ ] **AC3** Given two repair records for the same unit, when the ledger is read, then each row still states which findings THAT record closed, so a per-record account is not lost to the per-unit roll-up

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
