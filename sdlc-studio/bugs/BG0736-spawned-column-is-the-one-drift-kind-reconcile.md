# BG0736: spawned-column is the one drift kind reconcile can detect but never repair, so every decomposition leaves permanent drift the doctrine forbids fixing by hand

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Evidence:** Reproduced on RFC0060 on 2026-09-21. `refine apply` then `refine add` minted EP0258 and EP0259 and wrote `Decomposed-into:` into the RFC. `reconcile detect` then reported `spawned-column RFC0060: add EP0258, EP0259 to the sdlc-studio/rfcs/_index.md cell for RFC0060 - the files already say so`. `reconcile apply`, `apply --scope rfcs` and `apply --scope indexes` each reported `changed 0 row(s)` and left the cell reading `--`. Drift went 0 -> 1 and cannot be returned to 0 by any command.
> **Verification depth:** conversational
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`reconcile detect` emits a `spawned-column` item whenever a request's index cell disagrees with the census of what names it as parent. Every other drift kind in `DRIFT_KINDS` has an `apply_*` writer behind it. This one has none: `spawned_column_drift` exists at reconcile.py:2055 and no `apply_spawned_column` exists anywhere. `apply` therefore reports `changed 0 row(s)` against an item `detect` keeps emitting, at every scope. The cell is in `_INDEX_OWNED_COLUMNS` as a projection the field-sync pass must not write, which is correct in itself - but nothing else was ever written to own it, so the column has a detector, a remedy hint, and no writer.

## Steps to Reproduce

1. Decompose any request with `refine apply --request <id> --breakdown <file>`.
2. Run `reconcile.py detect` - one `spawned-column` item for that request.
3. Run `reconcile.py apply`, then `apply --scope rfcs`, then `apply --scope indexes` - each reports `changed 0 row(s)`.
4. Run `detect` again - the item is unchanged.

## Proposed Fix

Give the column a writer that derives it from `children_of`, the same census the detector compares against, run from `apply` at the request scopes. Keep it out of the field-sync pass - the exclusion in `_INDEX_OWNED_COLUMNS` is right and the reason it is right is that this cell needs a DEDICATED writer, exactly as `status` has `apply_type`.

## Acceptance Criteria

- [x] **AC1: a stale cell is brought up to date and the sweep can reach zero drift.**
  - **Given** a request index whose spawned cell reads `--` and a child file naming that request as parent
  - **When** `apply_spawned_column` runs
  - **Then** the cell holds the child's id and `spawned_column_drift` returns empty
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnIsRepairableTests::test_a_stale_cell_is_brought_up_to_date
  - **Verified:** yes (2026-09-21)
- [x] **AC2: a cell claiming work the census cannot see is HELD, never rewritten.**
  - **Given** a cell naming an id no file records an upward link to
  - **When** the writer runs
  - **Then** the cell is unchanged, the id is reported in `held`, and nothing is synced - the cell may be the only surviving record of the link, so deriving it from the census would delete evidence rather than correct it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnIsRepairableTests::test_a_cell_claiming_work_the_census_cannot_see_is_held_not_rewritten
  - **Verified:** yes (2026-09-21)
- [x] **AC3: the SHIPPED `apply` clears it.**
  - **Given** a tree carrying one spawned-column drift item
  - **When** `reconcile.py apply` is run as a subprocess
  - **Then** it names the synced cell on stdout and the detector then finds nothing - the wiring is the half a library test cannot see, and this kind had a working detector while `apply` called nothing for it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnIsRepairableTests::test_the_shipped_apply_clears_it
  - **Verified:** yes (2026-09-21)
- [x] **AC4: the rest of the row survives an escaped pipe.**
  - **Given** a row whose title cell carries a literal escaped pipe
  - **When** the cell is rewritten
  - **Then** the row still splits into the same number of cells and the title keeps its escape
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnIsRepairableTests::test_the_rest_of_the_row_survives_an_escaped_pipe
  - **Verified:** yes (2026-09-21)
- [x] **AC5: a scoped apply does not reach another type's index.**
  - **Given** both an RFC and a CR index carrying drift
  - **When** the writer runs with `types=["rfc"]`
  - **Then** the CR index is byte-identical and only the RFC cell moves
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnIsRepairableTests::test_a_scoped_apply_does_not_reach_another_type_s_index
  - **Verified:** yes (2026-09-21)
- [x] **AC6: the repair is idempotent.**
  - **Given** a tree the writer has already corrected
  - **When** it runs again
  - **Then** it syncs nothing and holds nothing - a writer that re-reports a row it already wrote makes every later sweep look dirty
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnIsRepairableTests::test_the_repair_is_idempotent
  - **Verified:** yes (2026-09-21)
- [x] **AC7: a dry run names the row and writes nothing.**
  - **Given** a tree carrying one spawned-column drift item
  - **When** the writer runs with `dry_run=True`
  - **Then** it returns the id it would sync and the index is byte-identical - a dry run that already wrote is the worst of both, reporting a plan and performing it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnIsRepairableTests::test_dry_run_names_the_row_and_writes_nothing
  - **Verified:** yes (2026-09-21)
- [x] **AC8: the JSON dispatch reports it too.**
  - **Given** the same tree
  - **When** `reconcile.py apply --format json` runs
  - **Then** its payload carries the synced id under `spawned_column` - `apply` has two dispatches and a writer wired into only one of them is a defect this module has shipped before
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnIsRepairableTests::test_the_json_apply_path_reports_it_too
  - **Verified:** yes (2026-09-21)
- [x] **AC9: a held cell is reported on stderr and drives the exit code.**
  - **Given** a cell naming work the census cannot see
  - **When** the shipped `apply` runs
  - **Then** it names the cell on stderr and exits non-zero - a disagreement the sweep could not resolve that exits 0 is invisible to the CI that runs this
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnIsRepairableTests::test_the_cli_reports_a_held_cell_and_exits_non_zero
  - **Verified:** yes (2026-09-21)
- [x] **AC10: the writer touches only the rows it was asked for.**
  - **Given** an index holding a row the census already agrees with, a continuation row carrying no id, and separately an index that never adopted the column
  - **When** the writer runs over each
  - **Then** none of those rows moves - the writer walks every row, so a default offset or a row keyed off any id in the line would write an epic id into whichever column sat there
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SpawnedColumnIsRepairableTests::test_the_writer_touches_only_the_rows_it_was_asked_for
  - **Verified:** yes (2026-09-21)

## Impact

Two costs, and the second is the expensive one. First, `refine` cannot leave the tree clean, so every decomposition raises the standing drift count by one and the number stops meaning anything. Second, the only remedy the tool names is to correct the cell, and AGENTS.md forbids hand-authoring `_index.md` because it is derived - so the tool instructs an action its own doctrine refuses, and the honest paths are to edit a derived file by hand or to carry the drift forever. BG0406 already fixed this detector's blindness and its false positives; it was never given a writer, so the corrected detector now reports true drift nothing can clear.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `reconcile.py`, empty the loop `apply_spawned_column` iterates so it writes nothing while still returning the ids - the pre-fix state, a detector firing into a sweep that cannot act | |
| AC2 | in `reconcile.py`, delete the `claimed - actual` hold branch from `apply_spawned_column` so every drifted cell is rewritten from the census | |
| AC3 | in `reconcile.py`, delete the `if do_spawned:` block from the TEXT dispatch of the apply command only, leaving the JSON one wired | |
| AC4 | in `reconcile.py`, swap `_split_row_cells` for `sdlc_md.table_cells` when rewriting the row, which unescapes a literal pipe | |
| AC5 | in `reconcile.py`, remove the `types` filter from `apply_spawned_column` so a scoped run rewrites every discovery index | |
| AC6 | in `reconcile.py`, replace `apply_spawned_column`'s loop over `spawned_column_drift` with its own walk of `_spawned_column_rows`, so `wanted` collects every request row rather than only the drifted ones | |
| AC7 | in `reconcile.py`, make `apply_spawned_column` fall through its `dry_run` early return so a rehearsal performs the write | |
| AC8 | in `reconcile.py`, delete the `spawned_column` entry from the JSON branch of the apply command so only the text dispatch calls the writer | |
| AC9 | in `reconcile.py`, replace the `unapplied += 1` after the held-cell message in the apply command with a bare `pass`, so the sweep exits 0 | |
| AC10 | in `reconcile.py`, drop the `rid not in by_id` skip from `apply_spawned_column` so every row in the index is rewritten from whatever the census says | |
| AC10 | in `reconcile.py`, widen `_spawned_column_rows` to key a row with `ID_SEARCH_RE.search(line)` instead of `search(cells[0])`, so any id mentioned anywhere in the row keys it | |
| AC10 | in `reconcile.py`, change `_spawned_column_rows` to set `col` to the last cell index when a header carries no spawned column, in place of leaving it None | |

## Coverage Rulings

| File | Line | Hash | Reason | Author | Date |
| --- | --- | --- | --- | --- | --- |
| .claude/skills/sdlc-studio/scripts/reconcile.py | 2169 | fb437d9ed0253a67 | unreachable by construction: the loop iterates the types spawned_column_drift emitted, and the detector already skipped any type whose ARTIFACT_TYPES entry resolves no directory - so rel is always truthy here. Kept as the writer's own guard rather than trusting a caller invariant, which is why it is ruled rather than deleted | sdlc-studio | 2026-09-21 |
| .claude/skills/sdlc-studio/scripts/reconcile.py | 2180 | fb437d9ed0253a67 | unreachable in practice: _spawned_column_rows already refused any row where col >= len(cells), counted with sdlc_md.table_cells, and_split_row_cells splits the same row on the same unescaped pipes. The guard survives because the two splitters are separate functions and a future divergence would otherwise write into a cell that does not exist - it cannot be reached to be tested without mutating one of them | sdlc-studio | 2026-09-21 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-09-21 | Claude Opus 5 | Fixed, and raised to High on the way: this was not a tidiness defect, it was a gate deadlock - the drift it leaves refuses every subsequent commit and the remedy it printed was an edit of a derived file the doctrine forbids. `apply_spawned_column` derives the cell from the same census the detector compares against, and only in the ADD direction; a cell naming work the census cannot see is held and reported, because that cell may be the only surviving record of the link. The pin logic is now one generator both the detector and the writer consume, so they cannot disagree about which cell holds the claim - a writer that counted columns separately would not merely miss a row, it would write an epic id over whichever column its own count landed on. |
