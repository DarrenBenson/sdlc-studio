# BG0611: The verdict ledger is re-parsed and re-annotated on EVERY lookup, so conformance spends 122 seconds making 374 million calls to judge 23 units

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional [[derived: criteria 2; plan rows 2; executed 2; killed 2; survived 0; not-run 0; entry point 0 of 2 criteria through the shipped CLI, 2 in-process | fp ae72f7a3576b ]] (the join is measured rather than timed - a counted 800-row, 32-record annotation, with the retired rows asserted beside the cost so an index that is fast and wrong cannot pass. NOT covered: the remaining conformance cost, which profiling puts in the corpus scan rather than the ledger and which is a separate finding)
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** cProfile over `gate._conformance('.', changed=False)` on 2026-08-25 at 91cd810b. Counted from the ledger: sdlc-studio/reviews/critic-verdicts.md holds 848 rows and 32 supersession records; plan-review-verdicts.md holds a further 116 rows. This is not corpus growth in artefacts - conformance judged only 23 units.
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_annotate_superseded` walks every verdict row against every supersession record, and it runs on every ledger lookup rather than once per process. Profiled over this workspace: `_matches_supersession` is called 16,837,139 times in a single whole-workspace conformance run, `sdlc_md.norm_id` 37,279,770 times, for 374 million calls and 122.7 seconds of wall clock to judge 23 units. The ledger holds 848 verdict rows and 32 supersession records - a cross-product of 27,136 - so 16.8M comparisons means the ledger is fully re-annotated about 620 times in one run. The cost is quadratic in the ledger and linear in the number of lookups, and both terms grow with every review this project records.

## Steps to Reproduce

Profile the lane directly: import gate.py and call `_conformance('.', changed=False)` under cProfile. Observed 2026-08-25 - 122.7s wall, 374,450,705 calls, with `critic.py::_matches_supersession` at 16,837,139 calls and 46.1s cumulative, and `lib/sdlc_md.py` id-normalisation at 37,279,770 calls and 40.1s. The pre-commit gate reports the same lane at 68s of a 45s budget on the scoped path, 123% over its baseline.

## Proposed Fix

Parse and annotate the ledger ONCE per process and reuse it, and index the supersession records by unit so the inner walk is a dict lookup rather than a scan. Normalising ids inside the comparison is the second multiplier: `_matches_supersession` calls `norm_id` twice per comparison, so 27,136 comparisons become 54,272 normalisations, repeated 620 times. Normalise once when the rows are read.

## Acceptance Criteria

- [ ] **AC1** Given a ledger of 800 verdict rows and 32 supersession records, when it is annotated, then id normalisation happens ONCE per row and once per record - fewer than 2,000 calls, not the 25,600 a cross-product costs. Counted in the test, never timed: a wall-clock assertion is a flake on a shared machine
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_annotating_the_ledger_normalises_each_row_and_record_once
- [ ] **AC2** Given the same ledger, when its rows are read back, then every row a supersession record names is marked retired with its reason, and no row it does not name is - an index that is fast and wrong is worse than the scan it replaced
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_the_annotation_still_marks_exactly_the_retired_rows

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `critic.py`, replace the index lookup in `_annotate_superseded` with a per-row scan over every record | Given a ledger of 800 verdict rows and 32 supersession records, when it is annotated, then id normalisation happens ONCE per row and once per record - fewer than 2,000 calls, not the 25,600 a cross-product costs. Counted in the test, never timed: a wall-clock assertion is a flake on a shared machine |
| AC2 | in `critic.py`, return the rows from `_annotate_superseded` without setting `superseded` on any of them | Given the same ledger, when its rows are read back, then every row a supersession record names is marked retired with its reason, and no row it does not name is - an index that is fast and wrong is worse than the scan it replaced |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Filed |
