# BG0873: reconcile reports a v3-keyed handoff file as an orphan index row

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
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

- [ ] **AC1** The behaviour described is corrected: For a handoff file keyed HO-<ulid>, reconcile.py detect reports orphan-row because `meta_census` and `_meta_index_row_ids` (reconcile.py:778-800) read only...
- [ ] **AC2** The proposed fix lands, pinned by a test: Read meta keys through `sdlc_md`'s id parser so both schemas resolve.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
