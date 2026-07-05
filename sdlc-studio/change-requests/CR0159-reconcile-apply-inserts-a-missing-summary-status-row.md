# CR-0159: reconcile apply inserts a missing summary status row instead of exiting 0 over a count-mismatch it created

> **Status:** Complete
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-05
> **Created-by:** sdlc-studio file

## Summary

A status flip into a status absent from the summary table (e.g. the first CR to reach Approved) leaves apply unable to reconcile the counts: it rewrites the data row, cannot insert the missing '| Approved | 1 |' summary row, and exits 0 while detect immediately reports a count-mismatch. Pre-existing behaviour (reproduced identically at baf603d with a plain Status header), surfaced by the 2026-07-D critic while verifying status-alias writer parity. apply should insert the missing canonical-vocab summary row (bounded to the reconcile-managed global summary block), or exit non-zero naming the residual - never a clean exit over drift it just created.

## Acceptance Criteria

- [ ] apply inserts a missing in-vocab summary status row in the reconcile-managed global summary block (the Total-row block), and detect-after is clean
- [ ] a scoped per-epic summary table is never touched (existing author-maintained-block guard regression-pinned)
- [ ] if the row cannot be inserted, apply exits non-zero naming the residual count-mismatch - no clean exit over self-created drift
- [ ] regression test seen RED first; CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-05 | audit | Raised |
| 2026-07-05 | Claude (sprint 2026-07-D addendum) | Delivered pre-release: _insert_missing_summary_rows in the managed global block (before Total), per-epic roll-ups untouched, unplaceable statuses warn + exit 1; transition index_synced honesty test re-pinned to the now-truthful True |
