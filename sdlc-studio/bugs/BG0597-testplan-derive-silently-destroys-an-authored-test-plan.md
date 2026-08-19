# BG0597: testplan derive silently DESTROYS an authored Test Plan row when a criterion carries more than one, at exit 0

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Depends on:** BG0596 - the reporting join and the destructive re-derive are the same criterion-keyed read in `_testplan_rows`; repairing the write path first would leave two definitions of what a plan holds
> **Evidence:** Found by the QA seat during the adversarial goal review of the 30-unit plan, 2026-08-19, and reproduced independently in a second throwaway fixture before filing.
> **Created:** 2026-08-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-18T20:35:22Z

## Summary

`verify_ac.testplan_derive` reads the existing plan through `_testplan_rows`, which keys by criterion, then writes one row per criterion through `_replace_testplan` - and `_replace_testplan` replaces the whole section. A Test Plan declaring two mutants for one criterion therefore comes back with one, and the command exits 0 with no warning. The row that survives is the LAST one parsed, so the author's first mutant is the one destroyed. BG0596 records the same criterion-keyed join as a REPORTING defect - `--from-plan` under-counts. This is the destructive half of the same key: the reporting path lies about what it ran, this path deletes what was authored.

## Steps to Reproduce

Reproduced 2026-08-19 in a throwaway fixture at $SCRATCH/fx. A bug artefact was written with two criteria and a three-row Test Plan: two rows on AC1 (mutants 'remove the dedupe branch' and 'replace the key with the criterion id') and one on AC2. `grep -c '^| AC'` reports 3 rows before. Running `verify_ac.py testplan derive --unit BG9001 --root <fixture>` prints `BG9001 -> 2 row(s) for 2 criteria` and EXITS 0. `grep -c '^| AC'` reports 2 rows after, and the surviving AC1 row is the SECOND mutant - the first is gone from the file with nothing printed about it. The guard at that site refuses only a plan the parser cannot read AT ALL; a plan it can partly read is overwritten with losses. Positive control: a plan with one row per criterion round-trips unchanged.

## Proposed Fix

Key the existing-plan read by (criterion, mutant) or by row index, matching the fix BG0596 makes to the reporting join, so the two callers of `_testplan_rows` cannot disagree about what a plan holds. Where a re-derive would drop an authored row, REFUSE rather than write - a derive that loses evidence must not exit 0. Report rows and criteria as two figures so a divergence is visible. Note that fixing `_testplan_rows` changes its return shape and `testplan_derive` is its other caller; pin that caller, or the repair moves the defect one construct over.

## Acceptance Criteria

- [ ] **AC1** Given a Test Plan carrying two rows on one criterion, when `verify_ac.py testplan derive` re-derives that unit, then both rows are present in the file afterwards and the `| AC` row count has not fallen
- [ ] **AC2** Given a re-derive that cannot carry an authored row forward, when the command runs, then it REFUSES with a non-zero exit and names the row it would have lost - a derive that loses evidence must not exit 0
- [ ] **AC3** Given the fixture reproduced on 2026-08-19 (two criteria, three rows, two of them on AC1), when `verify_ac.py testplan derive` is driven through the shipped CLI by subprocess, then the file holds 3 rows before and 3 rows after, and the first AC1 mutant is still the first AC1 mutant
- [ ] **AC4** Given a Test Plan with exactly one row per criterion, when derive runs, then the section round-trips unchanged and the exit is 0 - the control proving the fix refuses only real losses
- [ ] **AC5** Given `_testplan_rows` with its changed return shape, when `testplan_derive` reads it, then a test pins that caller specifically - the repair does not relocate the defect into the sibling that shares the helper

## Impact

This is the command the delivery gate instructs every in-scope unit to run - 29 of the 30 units in the batch now being planned. A criterion that can be wrong in several distinct ways is exactly the one worth pinning several times, so the loss falls hardest on the best-authored plans. The evidence is destroyed silently and on the happy path: the operator sees exit 0 and a plausible row count. A mutant that was authored, reviewed and then deleted by the tool is indistinguishable afterwards from one that was never written.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Groomed: acceptance criteria authored so the unit is plannable |
| 2026-08-19 | sdlc-studio | Scope widened: `mutation.plan_execution` is a THIRD caller of `_testplan_rows` and was undeclared, so the repair could relocate into a file the review may not read |
