# BG0406: Three units delivered nothing: BG0372 writes no velocity column, BG0359's detector is inert and would be wrong, and BG0357's consumer key was wrong

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
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

- [x] **AC1: the velocity term is the number the close report printed, from the same components.**
  - **Given** a run whose gate time, mutation time and review time are all recorded, so that
    supplying the components and blanking them give different answers
  - **When** `retro._overhead_terms` computes the ratio for that batch
  - **Then** it equals `sprint_report.report(...)["overhead"]["ratio"]`, and the test asserts
    the blanked call gives something else, so it cannot pass on a fixture that cannot tell them
    apart. The mutant: pass `{}` for either component in the call `_overhead_terms` makes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityOverheadTermAgreesWithTheCloseTests::test_the_velocity_term_is_the_number_the_close_reports
  - **Verified:** yes (2026-08-11)

- [x] **AC2: the row says whether that ratio is exact or a floor.**
  - **Given** a sprint whose every overhead component is measured, and the same sprint with its
    mutation series emptied
  - **When** the terms are computed
  - **Then** the first records `exact` and the second `lower`, because a floor measured from one
    component of three is not the same quantity as an exact figure and this file is read row
    against row. The mutant: return the bound as `exact` regardless of what the report said.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityOverheadTermAgreesWithTheCloseTests::test_the_row_records_whether_the_ratio_is_exact_or_a_floor
  - **Verified:** yes (2026-08-11)

- [x] **AC3: no term in the row is an arithmetic residue that can only be zero.**
  - **Given** the close report's own figures for a measured sprint
  - **When** `total - overhead - delivery` is evaluated on them
  - **Then** it is exactly 0, because delivery is DEFINED as `total - overhead` - so the terms
    are the ratio and its bound and nothing else, and no column named `Unattributed` remains in
    the shipped header. The mutant: reinstate `unattributed_s` in `_overhead_terms`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityOverheadTermAgreesWithTheCloseTests::test_no_term_is_a_residue_that_can_only_be_zero
  - **Verified:** yes (2026-08-11)

- [x] **AC4: the spawned-work detector finds its column past a Summary table.**
  - **Given** a discovery index in the shape every real one has - a `## Summary` status/count
    table, then the data table - carrying one stale cell
  - **When** `spawned_column_drift` runs over it
  - **Then** the stale cell is reported, where before the column position was pinned from the
    summary block and every data row was skipped. The mutant: pin the header once, at the first
    table in the file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnPastTheSummaryTableTests::test_the_column_is_found_past_a_summary_table
  - **Verified:** yes (2026-08-11)

- [x] **AC5: a true cell is not reported as drift, for the link spellings this corpus writes.**
  - **Given** an index cell naming a CR that links upward with `> **RFC:** RFC-0001`, the
    spelling 20 artefacts here use and none of them pairs with `Parent:`
  - **When** the detector censuses that request's children
  - **Then** the cell agrees with the census and nothing is reported. The mutant: drop the
    `rfc_ref` limb from `child_parent`. Measured over the full historical RFC index of 57 rows,
    that mutant reports 16 rows of which 7 name links the census cannot see.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnPastTheSummaryTableTests::test_a_child_linked_by_the_rfc_field_is_not_drift
  - **Verified:** yes (2026-08-11)

- [x] **AC6: a cell claiming work no file links back is never told to blank itself.**
  - **Given** a cell naming an id the census cannot see
  - **When** the drift item is composed
  - **Then** the remedy names that id and says to record the link in the child file, warning
    that the cell may be the sole record of it - while a cell the census can see PAST is still
    simply brought up to date. The mutant: restore the single "correct it from the census"
    remedy, which reads as an instruction to delete the evidence.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnPastTheSummaryTableTests::test_an_over_claiming_cell_is_not_told_to_blank_itself
  - **Verified:** yes (2026-08-11)

- [x] **AC7: the sweep prints the item instead of dying on it.**
  - **Given** an index that produces a spawned-column drift item
  - **When** `reconcile.py detect` runs over it
  - **Then** it prints the item and exits 1, where before it exited on `error: 'fix'` - the item
    named its advice `remedy` while the printer and every other item use `fix`, a crash
    unreachable only for as long as the detector found nothing. The mutant: name the key
    `remedy` again.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnPastTheSummaryTableTests::test_the_sweep_prints_the_item_rather_than_dying_on_it
  - **Verified:** yes (2026-08-11)

- [x] **AC8: a sign-off is not recorded against a unit that has not been delivered.**
  - **Given** a story at a non-terminal, pre-delivery status named in an approved batch
  - **When** `critic signoff --from-run` fans out over that batch
  - **Then** the unit is withheld and named, rather than taking a row that reads as approval of
    work that does not exist. Delivered by RUN-01KYPZ1G; the mutant is to take the batch as the
    scope without consulting each unit's status.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ASignoffSkipsAUnitThatDeliveredNothingTests::test_an_undelivered_STORY_is_still_withheld
  - **Verified:** yes (2026-08-11)

## The sign-off fan-out repeats the same shape

Closing RUN-01KYNKDP demonstrated the tooling half of this bug. `critic signoff --from-run` takes the run's APPROVED BATCH as its scope and writes a row for every id in it without consulting status. BG0372 and BG0359 had been reopened precisely because they deliver nothing, and US0553 was reverted to Blocked - and all three took a sign-off row naming the reviewer of record.

The note is batch-scoped, so it states no falsehood about those units specifically. The ROW still reads as approval of work that does not exist, which is the same defect as a status asserting a repair that did not happen: a record meaning less than it appears to. A sign-off should skip a non-terminal unit, or say that it included one.

## Impact

Three units marked Fixed that deliver nothing is worse than three units left open: the record asserts a repair that did not happen, in a project whose entire argument is that its records mean something. BG0359 is the sharper one - inert today, and actively destructive the moment somebody fixes the header pinning without also fixing the census.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
| 2026-08-11 | Claude Opus 5 | The REMAINING halves are fixed and the criteria were rewritten to name the production change each one must fail on - the tool-derived list restated the finding and stated nothing a test could redden. The velocity term now comes from one entry point that supplies every overhead component, so it is the number the close report printed rather than a smaller one computed from a third of the evidence; the unattributed span is gone, because delivery is defined as the measured span minus the measured overhead and a residue of the three is zero by construction, and the row records the ratio's BOUND instead. The spawned-work detector re-pins its column at any header carrying an ID cell, so a Summary table no longer blinds it, and `children_of` reads the `RFC:` field this corpus writes - measured over the full historical index of 57 rows, that removes 7 rows of false drift from 16. The remedy now distinguishes a cell the census can see past from one naming a link no file records, which it no longer offers to blank. BG0372 and BG0359 stay `Fixed` and are now true. |
| 2026-07-29 | Claude Opus 5 (RUN-01KYPZ1G) | The SIGN-OFF FAN-OUT half is FIXED and the bug stays OPEN for the rest. `critic signoff` now reads each unit's status and SKIPS a non-terminal one, naming it on stderr - closing the previous run wrote three rows against units that delivered nothing (two bugs reopened for exactly that reason, one story reverted to Blocked), and a row reading as approval of work that does not exist is the same defect as a status asserting a repair that did not happen. An unreadable unit reports cannot-say and proceeds, because refusing a sign-off over an unreadable file would make the check more important than the thing it guards. STILL OPEN: the velocity row's overhead ratio and unattributed span, `_overhead_terms` agreeing with the close report, `spawned_column_drift` finding its column past a Summary table, and the three units' statuses reflecting what they actually deliver. |
