# BG0956: transition set reports index synced but leaves archived index rows stale, and reconcile apply refuses them

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, changelog.d/BG0956.md
> **Evidence:** homelab 2026-10-06: 94-bug close batch; 31 archive rows hand-synced afterwards
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T17:18:27Z

## Summary

Closing 94 Fixed bugs in homelab with `transition.py set --id ... --status Closed` (skill 6.1.0+12) printed `index synced=True` for every unit, but 31 of them have their row in the archive sub-index (sdlc-studio/bugs/archive/v1.0.0/bug.md, written by archive.py), and those rows still read `Fixed`. `reconcile detect` then reports 31 status-mismatch plus a count-mismatch, and `reconcile apply` changes 0 rows: 'row not in a rewritable layout; edit it by hand'. The archive table has the same header as the live index (ID | Title | Severity | Priority | Status | Epic | Story | Created), so the layout is not exotic - the writers simply do not cover archive files while the census (`parse_index`'s union) does read them. Net effect: every transition of an archived unit creates drift that only a hand edit clears, and the sync flag claims otherwise.

## Steps to Reproduce

1. archive.py archive --type bug --release v1.0.0 with some Fixed rows
2. transition.py set --id <archived Fixed bug> --status Closed -> 'index synced=True'
3. The archive row still says Fixed; reconcile detect -> status-mismatch
4. reconcile apply -> 'could not apply ... row not in a rewritable layout; edit it by hand'

## Proposed Fix

Teach the index row writer used by transition and reconcile apply to locate a unit's row in archive sub-indexes too (the same union `parse_index` reads), and make `index synced` false when no row was written. Add a test with an archived row.

## Acceptance Criteria

- [ ] **AC1** Given a bug whose row `archive.py` moved into `archive/<release>/bug.md`, when `transition.py set` moves it Fixed -> Closed, then the archived row reads Closed, the summary counts agree, the output reports `index synced=True`, and `reconcile detect` reports no drift for it. Fails on: writing only the live index (today), or setting the flag without writing the row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ArchivedRowSyncTests::test_closing_an_archived_bug_rewrites_its_archive_row
- [ ] **AC2** Given an archived row already out of step with its file, when `reconcile apply` runs, then it rewrites that row and counts it as changed, never "row not in a rewritable layout". Fails on: the apply path still skipping archive sub-indexes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ArchivedRowApplyTests::test_apply_rewrites_a_stale_archived_row
- [ ] **AC3** Given an artefact with both a live row and an archived row, then the live row is the one written and the archived row is left as it is, as the census reads them (live wins). Fails on: rewriting both, or the archive first
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ArchivedRowApplyTests::test_a_live_row_wins_and_the_archive_is_untouched
- [ ] **AC4** Given a row no writer can place (a header-less table), then `transition.py set` still reports `index synced=False` and `reconcile apply` still names it. Fails on: the archive search turning an unplaceable row into a claimed sync
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ArchivedRowApplyTests::test_an_unplaceable_row_still_reports_unsynced

## Triage

- Reproduced 2026-10-06 against HEAD (99538064) and the installed copy, in a fixture whose archive `archive.py` wrote: the archived row stays Fixed after the transition, and `reconcile apply` refuses it with "row not in a rewritable layout".
- Not reproduced: the claim that `transition.py` printed `index synced=True`. Both copies print `index synced=False` with the warning "the artifact may be archived", single id and batch alike; the honest flag has existed since 290c6cfc. The defect that stands is that no writer reaches an archived row, so every transition of an archived unit leaves drift only a hand edit clears.
- Third casualty of the row archive, beside BG0955 (a test reading only the live index) and BG0957 (a negative control needing a live row). Build fixtures with `archive.archive`, as BG0955's tests do, so the rows are the shapes the product writes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Filed |
| 2026-10-06 | Claude Opus 5.5 (triage) | Groomed: reproduced against HEAD; the synced=True claim did not reproduce and is recorded as such; tool-derived criteria replaced with four executable ones; changelog fragment added to Affects |
