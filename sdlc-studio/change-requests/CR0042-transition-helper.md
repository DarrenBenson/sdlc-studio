# CR-0042: deterministic status-transition helper

> **Status:** Complete
> **Priority:** Medium
> **Type:** Feature
> **Requester:** Darren Benson
> **Date:** 2026-06-21
> **Affects:** scripts/transition.py (new), reference-scripts.md, SKILL.md
> **Depends on:** CR0026 (reconcile apply - the index sync it reuses)
> **GitHub Issue:** --

## Summary

Closes the last deterministic-tooling gap: the write-side status-transition cascade was
still hand-driven (set the file's `Status`, update its index row, recompute the summary
counts, tick the epic's breakdown checkbox - done ~40 times by hand this session).
`transition.py set --id <ID> --status <new>` does it deterministically, reusing the
tested `reconcile.apply_type` for the index sync rather than bespoke row editing.

## Proposed Changes

- `scripts/transition.py`: find the artifact, validate the new status against the type
  vocabulary, set its `Status` field (blockquote or inline `·` form, value-only),
  `apply_type` to sync the index row + counts, and for a story tick/untick its checkbox
  in the parent epic's Story Breakdown. `index_synced` reflects the true post-state
  (warns when a row is archived or the new status has no summary row); `--dry-run`.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/transition.py | status transition + index/epic cascade | New |
| reference-scripts.md, SKILL.md | catalogue + router | Modified |

### Breaking Changes

None. New helper.

## Acceptance Criteria

- [x] `set --id --status` sets the file Status (value-only, blockquote + inline forms), syncs the index row + counts, and ticks/unticks a story's epic-breakdown checkbox; `reconcile detect` is then clean.
- [x] Validates the status against the type vocabulary; raises on unknown id / no Status field; `--dry-run` writes nothing.
- [x] `index_synced` is honest - false (with a warning) when the row is archived or the new status has no summary row, rather than falsely claiming success.
- [x] Unit-tested incl. those honesty edges, non-story types, and a missing epic; independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0042) | Complete - transition.py; critic APPROVE after making index_synced reflect the real post-state |
