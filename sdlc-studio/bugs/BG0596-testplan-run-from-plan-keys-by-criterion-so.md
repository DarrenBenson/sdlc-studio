# BG0596: testplan run --from-plan keys by criterion, so a second mutant on the same AC is silently dropped

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
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

- [ ] **AC1** The behaviour described is corrected: `verify_ac._testplan_rows` builds a mapping keyed by criterion, so a Test Plan declaring more than one mutant for the same AC keeps only one.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Measured 2026-08-19 by a review of BG0592.
- [ ] **AC3** The proposed fix lands, pinned by a test: Key the join by (criterion, mutant) or by row index, so every declared row is a planned mutant.

## Impact

The done-gate reads this join to decide whether a unit's planned mutants were executed. A silently dropped row is a mutant nobody ran, reported as one that passed - which is the same false-green shape the mutation lane exists to remove, one level up.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Filed |
