# BG0596: testplan run --from-plan keys by criterion, so a second mutant on the same AC is silently dropped

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/help/mutation.md
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

- [ ] **AC1** Given a Test Plan declaring two mutants for one criterion, when `verify_ac._testplan_rows` builds the join, then the number of entries it returns equals the criterion-row count a plain text scan of the same file reports - asserted against that independent reader, never against the repaired function's own idea of what it holds
- [ ] **AC2** Given that plan with a kill registered for EVERY declared row - `cmd_from_plan` prints its planned figure only on the all-executed branch, so a partly-executed fixture asserts against absent output - when `mutation.py run --from-plan` reports, then the planned count equals the number of declared ROWS, not the number of distinct criteria
- [ ] **AC3** Given the mutation ledger, when a mutant is registered against a unit, then the record carries a ROW identity and not only `unit` plus `criterion`, so two mutants on one criterion are distinguishable on the record - and an existing entry with no row key still reads back rather than being orphaned
- [ ] **AC4** Given a plan carrying two rows on a criterion of which only one was executed, when `transition._planned_mutant_gate` reads the join, then it refuses and NAMES the unexecuted row - today it appends one sentence per CRITERION and drops the mutant text, so two rows on AC13 print the same sentence twice and identify neither
- [ ] **AC5** Given BG0592's artefact, when `--from-plan` runs against it end to end, then the planned count it prints equals the criterion-row count scanned directly from that file - the same production mutant as AC2, declared here as its instance over a real artefact rather than counted as a second mutant
- [ ] **AC6** Given a plan with exactly one row per criterion, when `--from-plan` runs, then its planned count is unchanged from today's - and the control must survive a join that double-counts, which is why adding the criterion back into the row key cannot be this row's mutant: on a single-row plan that leaves the count identical, so it is equivalent by construction
- [ ] **AC7** Given a Test Plan whose row count and criterion count differ, when `mutation.py`'s report prints - including on the REFUSAL branch, which prints neither figure today - then it states both, so a future divergence is visible rather than silent
- [ ] **AC8** Given the plan-review brief and the mutation help page, when a multi-row plan becomes legal, then both say so: `critic._plan_review_brief` hard-codes "one row per criterion" into the brief handed to every future plan reviewer, and `help/mutation.md` documents the worst verdict as held per criterion - a format change the shipped guidance contradicts is one nobody will use

## Impact

The done-gate reads this join to decide whether a unit's planned mutants were executed. A silently dropped row is a mutant nobody ran, reported as one that passed - which is the same false-green shape the mutation lane exists to remove, one level up.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, revert `_testplan_rows` to a single-assignment dict | Given a Test Plan declaring two mutants for one criterion, when `verify_ac._testplan_rows` builds the join, then the number of entries it returns equals the criterion-row count a plain text scan of the same file reports - asserted against that independent reader, never against the repaired function's own idea of what it holds |
| AC2 | in `mutation.py`, replace the row tally with a set of criterion ids | Given that plan with a kill registered for EVERY declared row - `cmd_from_plan` prints its planned figure only on the all-executed branch, so a partly-executed fixture asserts against absent output - when `mutation.py run --from-plan` reports, then the planned count equals the number of declared ROWS, not the number of distinct criteria |
| AC3 | in `mutation.py`, revert the record to two keys | Given the mutation ledger, when a mutant is registered against a unit, then the record carries a ROW identity and not only `unit` plus `criterion`, so two mutants on one criterion are distinguishable on the record - and an existing entry with no row key still reads back rather than being orphaned |
| AC4 | in `transition.py`, drop the row identity from the refusal and emit one line per criterion | Given a plan carrying two rows on a criterion of which only one was executed, when `transition._planned_mutant_gate` reads the join, then it refuses and NAMES the unexecuted row - today it appends one sentence per CRITERION and drops the mutant text, so two rows on AC13 print the same sentence twice and identify neither |
| AC5 | unnameable: this row exercises AC2's change to `mutation.py` end to end over a real artefact rather than naming a second one to make; its value is the corpus instance, and AC2's mutant already falsifies the production behaviour. The mention of a path and of `make` is forced by BG0600, not meant | Given BG0592's artefact, when `--from-plan` runs against it end to end, then the planned count it prints equals the criterion-row count scanned directly from that file - the same production mutant as AC2, declared here as its instance over a real artefact rather than counted as a second mutant |
| AC6 | in `verify_ac.py`, duplicate every row entry under its criterion id as well | Given a plan with exactly one row per criterion, when `--from-plan` runs, then its planned count is unchanged from today's - and the control must survive a join that double-counts, which is why adding the criterion back into the row key cannot be this row's mutant: on a single-row plan that leaves the count identical, so it is equivalent by construction |
| AC7 | in `mutation.py`, delete the print on the refusal path | Given a Test Plan whose row count and criterion count differ, when `mutation.py`'s report prints - including on the REFUSAL branch, which prints neither figure today - then it states both, so a future divergence is visible rather than silent |
| AC8 | in `critic.py`, restore the hard-coded sentence at `_plan_review_brief` | Given the plan-review brief and the mutation help page, when a multi-row plan becomes legal, then both say so: `critic._plan_review_brief` hard-codes "one row per criterion" into the brief handed to every future plan reviewer, and `help/mutation.md` documents the worst verdict as held per criterion - a format change the shipped guidance contradicts is one nobody will use |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Groomed: acceptance criteria authored so the unit is plannable |
| 2026-08-19 | sdlc-studio | Scope widened: `mutation.plan_execution` is the SECOND caller of `_testplan_rows`; the ledger keys by criterion, so the row identity AC3 needs is a schema change outside the original surface. Re-pointed 2 -> 3 |
| 2026-08-19 | sdlc-studio | Criteria re-pointed: AC1/AC5 assert against an independent reader rather than the repaired function or a literal, and the ledger row identity AC3 needs is stated as its own criterion |
| 2026-08-19 | sdlc-studio | Plan review F22: the helper has exactly TWO callers, not three. The caller named is right; the count was taken from a review and restated without checking |
| 2026-08-19 | sdlc-studio | Plan review REJECT: AC4 needs `transition.py`, AC8 added for the brief and help page that still teach one-row-per-criterion, AC6's mutant replaced (adding the criterion to the key is EQUIVALENT on a single-row plan), AC2 given a fixture that produces output to assert on. Re-pointed 3 -> 5 |
