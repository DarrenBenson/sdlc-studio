# BG0596: testplan run --from-plan keys by criterion, so a second mutant on the same AC is silently dropped

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Created:** 2026-08-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-18T20:35:22Z

## Summary

`verify_ac._testplan_rows` builds a mapping keyed by criterion, so a Test Plan declaring more than one mutant for the same AC keeps only one. `mutation.py run --from-plan` then reports fewer planned mutants than the table declares and reports `every one executed and killed` while never having looked at the others. A criterion that can be wrong in several distinct ways is exactly the one worth pinning several times, so the collapse falls hardest where the evidence matters most.

## Steps to Reproduce

Measured 2026-08-19 by a review of BG0592. Its Test Plan declares 18 rows across 15 criteria - AC13 carries four, because subtracting a subset, counting manual criteria as green, and emitting the clause unconditionally are distinct defects. `mutation.py run --story BG0592 --from-plan` reports 15 planned mutants, one per criterion, and prints `every one executed and killed`. BG0584 shows the same shape: 7 declared rows across 5 criteria, `--from-plan` joins 5. The extra rows are not reported as dropped; they are invisible.

## Proposed Fix

Key the join by (criterion, mutant) or by row index, so every declared row is a planned mutant. Where a criterion carries several, the gate should require all of them accounted for rather than any one. Report the count of rows alongside the count of criteria so the two cannot silently disagree, and pin the multi-row case with a test - a single-row-per-criterion fixture cannot see this, which is why nothing did.

## Acceptance Criteria

- [ ] **AC1** Given a Test Plan declaring two mutants for one criterion, when `verify_ac._testplan_rows` builds the join, then the number of entries it returns equals the criterion-row count a plain text scan of the same file reports - asserted against that independent reader, never against the new function's own idea of what it holds
- [ ] **AC2** Given that plan, when `mutation.py run --from-plan` reports its planned count, then the count equals the number of declared ROWS, not the number of distinct criteria
- [ ] **AC3** Given the mutation ledger, when a mutant is registered against a unit, then the record carries a ROW identity and not only `unit` + `criterion`, so two mutants on one criterion are distinguishable on the record - and an existing entry with no row key still reads back rather than being orphaned
- [ ] **AC4** Given a plan carrying two rows on a criterion of which only one was executed, when the done-gate reads the join, then it refuses and NAMES the unaccounted row - `every one executed and killed` is not printed while a declared row is unexecuted
- [ ] **AC5** Given BG0592's own Test Plan, when `--from-plan` runs against it, then the planned count it prints equals the criterion-row count scanned directly from BG0592's artefact - measured from the file, not asserted as the literal 18, so the criterion survives a repair that legitimately changes the row count
- [ ] **AC6** Given a plan with exactly one row per criterion, when `--from-plan` runs, then its planned count is unchanged from today's - the control proving the fix does not inflate the single-row case
- [ ] **AC7** Given a Test Plan whose row count and criterion count differ, when the report prints, then it states both figures, so a future divergence is visible rather than silent

## Impact

The done-gate reads this join to decide whether a unit's planned mutants were executed. A silently dropped row is a mutant nobody ran, reported as one that passed - which is the same false-green shape the mutation lane exists to remove, one level up.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `test_verify_ac.py`, assert against the parser's own return value | Given a Test Plan declaring two mutants for one criterion, when `verify_ac._testplan_rows` builds the join, then the number of entries it returns equals the criterion-row count a plain text scan of the same file reports - asserted against that independent reader, never against the new function's own idea of what it holds |
| AC2 | in `mutation.py`, replace the row tally with a set of criterion ids | Given that plan, when `mutation.py run --from-plan` reports its planned count, then the count equals the number of declared ROWS, not the number of distinct criteria |
| AC3 | in `mutation.py`, revert the record to two keys | Given the mutation ledger, when a mutant is registered against a unit, then the record carries a ROW identity and not only `unit` + `criterion`, so two mutants on one criterion are distinguishable on the record - and an existing entry with no row key still reads back rather than being orphaned |
| AC4 | in `mutation.py`, widen the gate to accept one execution per criterion | Given a plan carrying two rows on a criterion of which only one was executed, when the done-gate reads the join, then it refuses and NAMES the unaccounted row - `every one executed and killed` is not printed while a declared row is unexecuted |
| AC5 | in `test_verify_ac.py`, replace the scan with a literal | Given BG0592's own Test Plan, when `--from-plan` runs against it, then the planned count it prints equals the criterion-row count scanned directly from BG0592's artefact - measured from the file, not asserted as the literal 18, so the criterion survives a repair that legitimately changes the row count |
| AC6 | in `verify_ac.py`, add the criterion back into the row key | Given a plan with exactly one row per criterion, when `--from-plan` runs, then its planned count is unchanged from today's - the control proving the fix does not inflate the single-row case |
| AC7 | in `verify_ac.py`, drop the row figure from the printed report | Given a Test Plan whose row count and criterion count differ, when the report prints, then it states both figures, so a future divergence is visible rather than silent |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Groomed: acceptance criteria authored so the unit is plannable |
| 2026-08-19 | sdlc-studio | Scope widened: `mutation.plan_execution` is a THIRD caller of `_testplan_rows`; the ledger keys by criterion, so the row identity AC3 needs is a schema change outside the original surface. Re-pointed 2 -> 3 |
| 2026-08-19 | sdlc-studio | Criteria re-pointed: AC1/AC5 assert against an independent reader rather than the repaired function or a literal, and the ledger row identity AC3 needs is stated as its own criterion |
