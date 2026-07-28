# BG0342: All four artefact indexes assert stale Last Updated stamps that no writer maintains

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/reference-reconcile.md, sdlc-studio/stories/_index.md, sdlc-studio/epics/_index.md, sdlc-studio/bugs/_index.md, sdlc-studio/change-requests/_index.md, sdlc-studio/rfcs/_index.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

The indexes are documented as fully derived and reconcile syncs rows and counts, but nothing maintains the Last Updated header, so each index claims a freshness up to five weeks older than rows it contains, and reconcile detect reports `drift_items`=0 because the stamp sits outside every drift check - a false metadata assertion in the ledger files agents are told to trust.

## Steps to Reproduce

Evidence (Line 3 (Last Updated header) in stories/, epics/, bugs/, and change-requests/ _index.md): stories/_index.md line 3 says 2026-06-20 vs rows dated 2026-07-27; epics 2026-07-16 vs 2026-07-27; bugs 2026-07-04 vs 2026-07-26; change-requests 2026-07-04 vs 2026-07-27.

## Proposed Fix

Have every index writer (artifact.py row insertion and reconcile apply) stamp Last Updated with today's date on any row change, and add a reconcile detect check flagging a header older than the newest row's Updated date.

## Acceptance Criteria

The stamp is judged against the newest date on the index's own rows, never against today: a
header behind its rows is a false claim, a header level with or ahead of them is an index
nothing has been added to. Judged against the clock, every index in every project would
re-drift at midnight and `apply` would rewrite files that had nothing new to say.

### AC1: a header behind its own newest row is drift

- **Given** a story index stamped 2026-06-20 carrying a row updated 2026-07-27
- **When** `detect` runs
- **Then** it reports `stale-index-stamp`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::StaleIndexStampTests::test_detect_flags_a_stamp_older_than_the_newest_row

### AC2: the finding names both dates

- **Given** the same index
- **When** the finding is read
- **Then** its fix line names the claimed date and the real one, so no second command is needed to see the gap
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::StaleIndexStampTests::test_the_finding_names_both_dates

### AC3: a header level with, ahead of, or absent from its rows is not flagged

- **Given** an index stamped after its newest row (and, separately, one carrying no stamp at all)
- **When** `detect` runs
- **Then** nothing is reported - an untouched index is not a stale one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::StaleIndexStampTests::test_a_stamp_ahead_of_the_rows_is_not_flagged

### AC4: an index with a single `Date` column is checked too

- **Given** the change-request layout (one `Date` column, not `Created` + `Updated`)
- **When** detect and apply run
- **Then** the stale stamp is flagged and restamped - reading only the story shape would exempt two of the four indexes filed here
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::StaleIndexStampTests::test_a_single_date_column_index_is_checked_too

### AC5: apply restamps the header from the rows

- **Given** the stale index
- **When** `reconcile apply` runs
- **Then** the header reads the newest row's date and the drift is gone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::StaleIndexStampTests::test_apply_restamps_the_header_from_the_newest_row

### AC6: the restamp settles - it is not re-applied on every run

- **Given** an index apply has already restamped
- **When** apply runs again
- **Then** it writes nothing and `index_derived_issues` is empty - a clock-stamped header would re-drift daily
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::StaleIndexStampTests::test_restamping_settles_it_is_not_re_applied_every_run

### AC7: apply announces the restamp it is about to make

- **Given** a stale index under `apply --dry-run`
- **When** the run reports
- **Then** it says it would restamp, and to what - never "changed 0 row(s)" over a file it is about to rewrite
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::StaleIndexStampTests::test_apply_announces_the_restamp_it_is_about_to_make

### AC8: the failure reaches the exit code

- **Given** a stale index
- **When** `reconcile detect` runs as the commit gate runs it
- **Then** it exits non-zero and prints the kind - visible, not buried in an advisory
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::StaleIndexStampTests::test_detect_exits_non_zero_on_a_stale_stamp

### AC9: a new row leaves the index freshly stamped

- **Given** a current index and a row appended through the shared index writer every mint uses
- **When** the append completes
- **Then** the header carries the new row's date - the writer, not a later sweep, keeps the claim true
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::StaleIndexStampTests::test_a_row_insert_leaves_the_index_freshly_stamped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
| 2026-07-28 | Claude Opus 5 (sprint RUN-01KYJZGZ) | Reproduced on the live workspace (5 indexes, not 4 - the RFC registry has it too), acceptance criteria authored, `stale-index-stamp` drift + apply restamp shipped, the five live indexes restamped |
