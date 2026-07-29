# BG0406: Three units delivered nothing: BG0372 writes no velocity column, BG0359's detector is inert and would be wrong, and BG0357's consumer key was wrong

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Evidence:** Independent review of RUN-01KYNKDP. BG0372: VELOCITY.md header and row emitter unchanged, `unattributed_s` is 0.0 by construction. BG0359: `spawned_column_drift` returns [] on every real index; unblinded it reports 16 TRUE cells as drift.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Three units of RUN-01KYNKDP are marked Fixed and deliver nothing. BG0357's half is repaired; these two are not.

**BG0372.** `record_velocity` computes `overhead_ratio` and `unattributed_s` into the row dict, and the row EMITTER renders no cell for either - `VELOCITY_HEADER` gained no column. Nothing reaches the file the measurement exists to survive in. Worse, `unattributed_s` is 0.0 by construction: `sprint_report` defines `delivery = total - overhead`, so `total - overhead - delivery` is identically zero - and the docstring says it must be absent rather than zero. And `_overhead_terms` calls `sprint_report._overhead_ratio(root, ids, {}, {})`, blanking two of the three components, so it computes a DIFFERENT, lower number than the close report - manufacturing precisely the disagreement its docstring claims to prevent. The two shipped tests assert `VELOCITY_COLUMNS` membership and parse a hand-written header the writer never emits.

**BG0359.** `spawned_column_drift` pins its header from the FIRST table in the file. Every discovery index opens with a `## Summary` table, so `col` is None and every data row is skipped: the detector is inert on every real index. Strip the Summary table and 19 items appear. Two correct implementations of this already exist in the same file - `_linked_epics_column` and `project_fields` - and the latter carries a comment explaining that it must re-pin at any header, because pinning once corrupted a second table. Unblinded it would also be WRONG: `children_of` has no reader for the `RFC:` field this repo uses for RFC-to-CR links, so it reports 16 true cells as drift and its remedy instructs the operator to blank them.

## Steps to Reproduce

1. `retro.record_velocity` a row, then read `VELOCITY.md`: no Overhead or Unattributed column, no value.
2. `reconcile.spawned_column_drift('.')` -> []. Remove the `## Summary` table from `rfcs/_index.md` -> 19 items, 16 of them naming true cells.

## Proposed Fix

BG0372: add the columns to `VELOCITY_HEADER` and the row emitter, take `unattributed` from a term that is not defined as the residue of the other two (or drop it), and pass the real execution and mutation components to `_overhead_ratio` rather than `{}`. Assert against the FILE, not against the constant.

BG0359: re-pin the header at any table row carrying an ID column, as `project_fields` does. Then teach `children_of` the `RFC:` field, or scope the detector to links `children_of` can actually see and SAY which - a detector that reports true cells as drift is worse than none.

## Acceptance Criteria

- [ ] A recorded velocity row carries the overhead ratio and the unattributed span in VELOCITY.md, asserted by reading the file back.
- [ ] The unattributed span is a measured quantity, not the arithmetic residue of the other two, or it is absent.
- [ ] `_overhead_terms` computes the same number the close report computes, from the same components.
- [ ] `spawned_column_drift` finds its column in an index whose first table is a Summary table.
- [ ] A true spawned-work cell is not reported as drift, for every parent-child link spelling this corpus uses.
- [ ] Each of the three units' status reflects what it actually delivers.

## Impact

Three units marked Fixed that deliver nothing is worse than three units left open: the record asserts a repair that did not happen, in a project whose entire argument is that its records mean something. BG0359 is the sharper one - inert today, and actively destructive the moment somebody fixes the header pinning without also fixing the census.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
