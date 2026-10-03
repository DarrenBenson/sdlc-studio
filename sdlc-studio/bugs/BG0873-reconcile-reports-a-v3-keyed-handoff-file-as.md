# BG0873: reconcile reports a v3-keyed handoff file as an orphan index row

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_meta_v3_keys.py, changelog.d/BG0873.md
> **Evidence:** US0978 QA review round 1 (RUN-01M3VF2J), pre-existing at c0718152
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T15:09:54Z

## Summary

For a handoff file keyed HO-<ulid>, reconcile.py detect reports orphan-row because `meta_census` and `_meta_index_row_ids` (reconcile.py:778-800) read only numeric keys. help/handoff.md says old handoff files reconcile cleanly, true only for numeric keys. Identical before US0978.

## Steps to Reproduce

1. A v3 project holding sdlc-studio/handoffs/HO-01J2ABCDEFGHJKMNPQRSTVWXYZ-x.md and its index row. 2. reconcile.py detect -> orphan-row.

## Proposed Fix

Read meta keys through `sdlc_md`'s id parser so both schemas resolve.

## Acceptance Criteria

- [ ] **AC1** Given a v3 project holding `sdlc-studio/handoffs/HO-01J2ABCDEFGHJKMNPQRSTVWXYZ-x.md` and an index row linking it, when `reconcile.py detect --root <fixture>` runs, then it reports no drift for that handoff.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_meta_v3_keys.py::MetaV3KeyTests::test_a_v3_handoff_is_not_an_orphan
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** HEAD reports `orphan-row HO-0001` for the row of a file that exists
- [ ] **AC2** Given the same index row with no file behind it, and beside it a numeric `HO0002-y.md` with its row, when detect runs, then it reports exactly one orphan row, naming the v3 id, and nothing for HO0002.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_meta_v3_keys.py::MetaV3KeyTests::test_a_missing_v3_handoff_is_still_named
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** a fix that silences every meta row, or names the v3 row by a truncated number

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (groomer) | Groomed: premise executed at 78ae6c43: `sdlc-studio/handoffs/HO-01J2ABCDEFGHJKMNPQRSTVWXYZ-x.md` with its own index row, `reconcile.py detect` -> `orphan-row HO-0001` (the ULID's leading digits read as a sequential number); criteria authored, Points and Affects set |
