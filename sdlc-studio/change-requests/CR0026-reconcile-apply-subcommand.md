# CR-0026: reconcile `apply` - mechanical index fixes behind --dry-run

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Autosprint (RFC0003)
> **RFC:** RFC-0003
> **Date:** 2026-06-20
> **Affects:** scripts/reconcile.py, reference-reconcile.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Spawned from RFC0003. Promote reconcile's mechanical apply out of prose and into
`reconcile.py` as an `apply` subcommand: it fixes the two index-level drift classes
deterministically - **status-mismatch** (set the index row's Status cell to the
file's status) and **count-mismatch** (recompute the summary counts from the rows) -
behind a `--dry-run` contract, with round-trip idempotency a tested property.

## Problem

The mechanical apply is currently Claude prose (~3-4k tokens re-derived per cadence
trigger) and the documented idempotency guarantee is false. This session hand-applied
these exact fixes ~30 times.

## Proposed Changes

### Item 1: `apply` subcommand (status-mismatch + count recompute)

**Priority:** High **Effort:** Medium

`reconcile.py apply [--scope] [--dry-run]` rewrites each drifted index row's Status
cell (positionally, by the table header) to the file's canonical status, then
recomputes the summary-table counts from the data rows. `--dry-run` reports the
changes without writing. Structural classes (missing-row, orphan-row, missing-index)
and CR-completion / PRD prose stay report-only (deferred / out of scope).

### Item 2: Idempotency as a tested property

**Priority:** High **Effort:** Low

Round-trip tests: detect -> apply -> detect is clean; a second apply writes nothing.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/reconcile.py | `apply` subcommand + apply_type/apply_all | New |
| reference-reconcile.md | document `apply` + the --dry-run contract; correct the idempotency claim | Modified |

### Breaking Changes

None. `detect` is unchanged; `apply` is new and gated behind an explicit subcommand.

## Acceptance Criteria

- [x] `apply` sets a drifted index row's Status to the file's status (positionally, by header) and recomputes the summary counts; `detect` is then clean.
- [x] `--dry-run` reports the would-be changes and writes nothing.
- [x] Idempotent: a second `apply` writes nothing (round-trip test detect->apply->detect clean).
- [x] Structural classes (missing-row/orphan-row/missing-index) are left report-only. Unit-tested.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0003) | Spawned from RFC0003 (reconcile apply); scoped to status-mismatch + count recompute |
| 2026-06-20 | Autosprint (RFC0003) | Also fixed `_table_cells` to respect escaped pipes (`\|` in a cell) - found while making apply write-safe; dropped consuming repo A stories drift 6->1 (BG0020 class) |
