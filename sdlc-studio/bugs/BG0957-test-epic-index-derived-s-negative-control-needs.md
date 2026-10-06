# BG0957: `test_epic_index_derived`'s negative control needs a live epic row with a count, so an archive that empties the live epic index turns it red

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/tests/test_epic_index_derived.py
> **Evidence:** Pre-push boundary gate on 65e36b98, 2026-10-06 (full-suite lane); reproduced at 2c72fe8e against 9f75496a.
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T18:29:59Z

## Summary

`test_every_row_is_derived_and_a_mutated_row_fails` mutates one row's Stories cell in a copy of the tree and asserts the sweep reports it. It picks that row with `next(...)` over the LIVE `epics/_index.md` only (tools/tests/`test_epic_index_derived.py`:114). The v6.1 archive (2c72fe8e) moved every epic row into `epics/archive/`, so no row qualified and `next` raised StopIteration: red at 2c72fe8e, green at 9f75496a. CI never showed it, because the skill suite failed first in the same step (run 37335339814) and tools/tests did not run. It passes at 443df8dd only because EP0274 is now live with a count, and the next archive that empties the live index turns it red again. `_epic_index_cells` reading only the live index is defensible, since archived rows are terminal; the defect is the test's assumption that a live row exists.

## Steps to Reproduce

git checkout 2c72fe8e; pytest tools/tests/`test_epic_index_derived.py` -> StopIteration at line 114. At 9f75496a: 7 passed.

## Proposed Fix

Make the negative control independent of what the live index happens to hold: when no live row qualifies, the copy builds one (for instance by moving an archived row, which the product's own writers produced, back into the copy's live table), so the mutation always has a target. Never skip the control.

## Acceptance Criteria

- [ ] **AC1** With a live epic index holding no epic row, every row archived, the negative control still mutates a row and the sweep reports exactly that row
  - **Verify:** pytest tools/tests/test_epic_index_derived.py::EpicIndexNegativeControlTests::test_an_emptied_live_index_still_has_a_target
- [ ] **AC2** With live rows present, the test behaves as it does today
  - **Verify:** pytest tools/tests/test_epic_index_derived.py::EpicIndexRepoTests::test_every_row_is_derived_and_a_mutated_row_fails

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Filed |
