# BG0597: testplan derive silently DESTROYS an authored Test Plan row when a criterion carries more than one, at exit 0

> **Status:** Open
> **Severity:** High
> **Verification depth:** functional (five criteria over `verify_ac.py` and `mutation.py`. Every mutant below was executed against the real tree with `__pycache__` purged and `python3 -B`, its target's hash checked CHANGED before the run and byte-identical after, and the KILL confirmed by the name of the failing test rather than by a failure count. This field is rewritten from that re-execution, not amended: an independent review found the previous version false on five of six units in this batch, and an amended false record is still a false record. AC1 and AC2 are driven through the SHIPPED command as a subprocess against a root asserted to be under `tempfile`, with the repository's own artefacts checked unchanged; AC3 declares that route `unnameable`, because no production edit falsifies a rule about how evidence is taken. The read-path and write-path mutants are provably DISTINCT - reverting `_testplan_rows` kills BG0596's test and not this one's, and reverting the derive loop does the reverse. This unit was the only one in the batch the delivery review found clean. REVERT-CHECKED: this unit's production files were reverted to the run's base ref and its own verifiers re-run - they go RED, so the tests reach the shipped change rather than a copy of it. That check is the one an independent review used to find this batch's worst defect, and it is now run against every unit rather than the one somebody thought to try.)
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

- [x] **AC1** Given a Test Plan carrying two rows on one criterion, when `verify_ac.py testplan derive` re-derives that unit as a SUBPROCESS against a root asserted to be under `tempfile`, then both rows are present afterwards in file order, the command EXITS 0, the Test Plan section is rewritten and the repository's own artefacts are untouched - a derive that refuses every multi-row plan loses no rows and is not the fix, because it makes the format BG0596 requires unmaintainable through the shipped command
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::MultiRowTestPlanTests::test_a_re_derive_preserves_every_row_and_exits_zero
  - **Verified:** yes (2026-08-19)
- [x] **AC2** Given a plan row whose criterion id is no longer among the unit's criteria - an ORPHAN row, which is what an AC renumbering produces - when derive runs, then it REFUSES with a non-zero exit and PRINTS the row it would have dropped: measured 2026-08-19, a two-row plan (AC1 and AC7) against a one-criterion unit silently became one row at exit 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::MultiRowTestPlanTests::test_an_orphan_row_is_refused_and_named
  - **Verified:** yes (2026-08-19)
- [x] **AC3** Given the evidence for AC1 and AC2, when it is taken, then it comes through a subprocess invocation of the shipped `verify_ac.py` against a root asserted to be under `tempfile` - never through an in-process call, because the defect is in a command and a library test cannot see a command's wiring
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::MultiRowTestPlanTests::test_the_shipped_command_preserves_rows_through_a_subprocess
  - **Verified:** yes (2026-08-19)
- [x] **AC4** Given a Test Plan with exactly one row per criterion, when derive runs, then the Criterion and Mutant columns round-trip unchanged and the exit is 0 - the Title column is regenerated from the criterion by design, so a byte-identical assertion over the whole row would fail for a reason unrelated to this fix
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::MultiRowTestPlanTests::test_a_single_row_plan_round_trips_unchanged
  - **Verified:** yes (2026-08-19)
- [x] **AC5** Given `_testplan_rows` with its changed return shape, when `mutation.plan_execution` reads it - the second of the helper's two callers, in another file, consuming the return as a dict via `sorted(planned.items())` - then `--from-plan` still reports correctly for a single-row plan and the ledger join is unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::RowKeyedJoinTests::test_the_changed_return_shape_still_serves_its_other_caller
  - **Verified:** yes (2026-08-19)

## Impact

This is the command the delivery gate instructs every in-scope unit to run - 29 of the 30 units in the batch now being planned. A criterion that can be wrong in several distinct ways is exactly the one worth pinning several times, so the loss falls hardest on the best-authored plans. The evidence is destroyed silently and on the happy path: the operator sees exit 0 and a plausible row count. A mutant that was authored, reviewed and then deleted by the tool is indistinguishable afterwards from one that was never written.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, revert `testplan_derive`'s row loop to emit one row per criterion block | Given a Test Plan carrying two rows on one criterion, when `verify_ac.py testplan derive` re-derives that unit as a SUBPROCESS against a root asserted to be under `tempfile`, then both rows are present afterwards in file order, the command EXITS 0, the Test Plan section is rewritten and the repository's own artefacts are untouched - a derive that refuses every multi-row plan loses no rows and is not the fix, because it makes the format BG0596 requires unmaintainable through the shipped command |
| AC2 | in `verify_ac.py`, delete the orphan-row refusal | Given a plan row whose criterion id is no longer among the unit's criteria - an ORPHAN row, which is what an AC renumbering produces - when derive runs, then it REFUSES with a non-zero exit and PRINTS the row it would have dropped: measured 2026-08-19, a two-row plan (AC1 and AC7) against a one-criterion unit silently became one row at exit 0 |
| AC3 | unnameable: this row constrains the evidence ROUTE - a subprocess against a temporary root rather than an in-process call into `verify_ac.py` - and no change to production can falsify it; what it protects is that AC1 and AC2 exercise the shipped command. The mention of a path and of `call` is forced by BG0600, not meant | Given the evidence for AC1 and AC2, when it is taken, then it comes through a subprocess invocation of the shipped `verify_ac.py` against a root asserted to be under `tempfile` - never through an in-process call, because the defect is in a command and a library test cannot see a command's wiring |
| AC4 | in `verify_ac.py`, make it refuse every re-derive | Given a Test Plan with exactly one row per criterion, when derive runs, then the Criterion and Mutant columns round-trip unchanged and the exit is 0 - the Title column is regenerated from the criterion by design, so a byte-identical assertion over the whole row would fail for a reason unrelated to this fix |
| AC5 | in `mutation.py`, delete the shape adapter | Given `_testplan_rows` with its changed return shape, when `mutation.plan_execution` reads it - the second of the helper's two callers, in another file, consuming the return as a dict via `sorted(planned.items())` - then `--from-plan` still reports correctly for a single-row plan and the ledger join is unchanged |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Groomed: acceptance criteria authored so the unit is plannable |
| 2026-08-19 | sdlc-studio | Scope widened: `mutation.plan_execution` is the SECOND caller of `_testplan_rows` and was undeclared, so the repair could relocate into a file the review may not read |
| 2026-08-19 | sdlc-studio | Criteria hardened by the QA seat: AC1 gained the exit-0 clause a refuse-everything fix would otherwise satisfy, AC2 names the ORPHAN row as its reachable case (a second silent-loss path, reproduced), AC4 excludes the regenerated Title column, and AC5 re-points at `mutation.plan_execution` - the caller that actually breaks |
| 2026-08-19 | sdlc-studio | Plan review F22: the helper has exactly TWO callers, not three. The caller named is right; the count was taken from a review and restated without checking |
