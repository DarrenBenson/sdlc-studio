# BG0435: the loading-guide path checker skips a whole table whose first column is the path, and nine of twelve broken-path shapes escape it

> **Status:** Fixed
> **Verification depth:** functional (before/after run over the shipped guide: 126 -> 127 path-bearing cells; both the path-column and label-column cases pinned)
> **Severity:** High
> **Points:** 3
> **Affects:** tools/check_links.py, tools/tests/test_check_links.py
> **Evidence:** Executed by an independent reviewer with thirteen probe cells and a live classification census (97 bare, 29 anchored, 13 prose, 11 templated, 0 invocation).
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`loading_guide_cells` iterates `cells[1:]` on the premise that column 0 is a task or flag label. The guide's second table is headed `| Path | Purpose |`, so its six path cells are never examined at all - repointing one at a non-existent file leaves the checker reporting `All markdown links resolve`, exit 0. Beyond that, only three of twelve probe shapes are caught: the `_INVOCATION` pattern matches its tokens ANYWHERE in a cell, so any path containing `rg`, `bash` or `npm` as a hyphen-delimited component is classified as an invocation and skipped (live, that pattern classifies ZERO cells - it only creates holes); `_PATH_CELL` allowlists six extensions, so `.txt`, `.toml` and `.ts` fall to prose; and whole-cell anchoring means a path with trailing prose, a directory, a glob and a titled markdown link are all skipped. The live guide already carries one such unchecked cell, and the AC's stated exemption list names only two of the three classes that actually exempt.

## Steps to Reproduce

1. On a copy of the skill, repoint a path in the `| Path | Purpose |` table at a missing file - `check_links.py` exits 0.
2. Inject `scripts/rg-wrapper-DOES-NOT-EXIST.py` as a guide cell - classified invocation, skipped.
3. Repoint `SKILL.md`'s `scripts/artifact.py (...)` cell at a missing file - exits 0.

## Proposed Fix

Classify a cell by whether it presents a path, not by its column index; anchor the invocation pattern to the start of the cell; widen the extension set or drop the allowlist in favour of a resolve-attempt; and name every exemption class in the criterion.

## Acceptance Criteria

### AC1: a path in column 0 is examined

- **Given** a Progressive Loading Guide table headed `| Path | Purpose |`
- **When** the sweep runs
- **Then** its column-0 paths are classified and checked, because the sweep skipped column 0 unconditionally and those cells are precisely what it exists to examine
- **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideColumnTests::test_a_path_column_zero_is_examined
- **Verified:** yes (2026-08-02)

### AC2: a label in column 0 is still skipped

- **Given** a table headed `| Task | Read |`
- **When** the sweep runs
- **Then** the task label is not read as a path, so the fix cannot be satisfied by examining every column and reporting a broken link for every row
- **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideColumnTests::test_a_label_column_zero_is_still_skipped
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
