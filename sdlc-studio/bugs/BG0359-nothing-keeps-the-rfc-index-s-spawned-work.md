# BG0359: Nothing keeps the RFC index's spawned-work column true once it has been backfilled

> **Status:** Open
> **Verification depth:** RETRACTED on reopen (was: functional (tests red-first)) - re-verify before a terminal status; the previous evidence was withdrawn, not lost
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, sdlc-studio/rfcs/_index.md, .claude/skills/sdlc-studio/templates/indexes/rfc.md
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery, split from BG0319); agent; skill v5.0.0

## Summary

BG0319's backfill corrected 33 false cells in the RFC index by deriving them from the RFC files. Nothing keeps them true: reconcile does not check the column, so the next decomposition leaves a stale cell exactly as before. The column header also still reads Spawned CRs while most cells now hold epic ids, and the header is fixed by the shipped index template and asserted by three test files, so renaming it is a cross-file change rather than an edit.

## Steps to Reproduce

Refine an RFC into an epic. Read the RFC index: its spawned-work cell for that RFC is unchanged. Run reconcile detect: it reports no drift, because the column is outside every check it performs.

## Proposed Fix

Derive the column in reconcile from the RFC files, preserving a cell the derivation cannot answer for rather than emptying it. Rename the header to match what the cells hold, which requires the shipped template and the three asserting test files to move together.

## Acceptance Criteria

### AC1: a stale spawned-work cell is reported

- **Given** an index cell holding a placeholder against a request with a real child
- **When** reconcile sweeps
- **Then** reconcile reports `spawned-column` drift naming both sides, so a cell that was true only on the day somebody swept it cannot rot unnoticed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnStaysTrueTests::test_a_stale_cell_is_reported
- **Verified:** yes (2026-07-29)

### AC2: a true cell is not

- **Given** a cell that matches the census
- **When** reconcile sweeps
- **Then** nothing is reported, because a detector that always fires is not a detector
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnStaysTrueTests::test_a_true_cell_is_not
- **Verified:** yes (2026-07-29)

### AC3: over-claiming is drift too

- **Given** a cell naming work that does not exist
- **When** reconcile sweeps
- **Then** it is reported - the column can be wrong by over-claiming as readily as by under-claiming, and a check looking only for missing ids would pass a fabrication
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnStaysTrueTests::test_a_cell_claiming_work_that_does_not_exist_is_reported
- **Verified:** yes (2026-07-29)

### AC4: the column is found under any of its names

- **Given** the header spellings projects use - this repo's says `Spawned CRs` while most of its cells hold epic ids, and renaming it is a cross-file change
- **When** reconcile sweeps
- **Then** each is recognised, so a detector keyed to one spelling does not silently exempt every project that named the column something else
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnStaysTrueTests::test_the_column_is_found_under_any_of_its_names
- **Verified:** yes (2026-07-29)

### AC5: the sweep calls it

- **Given** `reconcile detect`
- **When** reconcile sweeps
- **Then** the kind appears in the sweep's drift, because a detector nothing calls reports nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnStaysTrueTests::test_the_sweep_includes_it
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery, split from BG0319) | Filed |
| 2026-07-29 | Claude Opus 5 | The column is now DERIVED-CHECKED rather than swept: `spawned_column_drift` compares each request's cell against `children_of` and reports either direction of disagreement. The header rename the finding notes as a cross-file change is deliberately NOT made - the detector reads a set of accepted spellings instead, so this project keeps its header and any project naming the column differently is covered on the day it does. |
| 2026-07-29 | Claude Opus 5 | REOPENED at the closing review. `spawned_column_drift` pins its header from the FIRST table in the file, and every discovery index opens with a `## Summary` table - so the column is never found and the detector is inert on every real index. Unblinded it would also be WRONG: `children_of` has no reader for the `RFC:` field this repo uses, so it reports 16 true cells as drift and its remedy says to blank them. Every fixture had a single table, which is why the tests passed. Marked Fixed while delivering nothing; the residue is BG0406. |
