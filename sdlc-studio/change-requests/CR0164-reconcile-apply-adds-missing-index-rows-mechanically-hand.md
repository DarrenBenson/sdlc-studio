# CR-0164: reconcile apply adds missing index rows mechanically - hand-authoring 23 rows is the tool's failure

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-05
> **Created-by:** sdlc-studio file

## Summary

Field report from a consuming project's bug-index reconcile: detect found 23 missing-row items plus 6 pre-existing orphan rows. apply was a no-op for both - missing-row is a report-only class - so the agent had to snapshot orphans, then HAND-AUTHOR 23 index rows matching the house table format, exactly the hand-editing the doctrine forbids and the toolchain exists to prevent. Additionally, apply cannot be scoped per-item, so a mixed drift report forces all-or-nothing. Proposed: apply appends missing rows via the same header-driven row writer artifact.py uses (sdlc_md.row_from_header + the index's own header, honouring the tolerant convention layer); rows it cannot place in an off-schema/header-less table are reported unapplied (fail loud, never guessed). Orphan rows stay report-only - removing history is a judgement call, never mechanical.

## Acceptance Criteria

- [ ] apply appends each missing-row item to the type's data table using the table's own header order; detect-after shows no missing-row for the appended ids
- [ ] an index whose data table the writer cannot pin (header-less/off-schema) reports the rows as unapplied and exits non-zero - never silent, never guessed, never hand-edit-by-default
- [ ] orphan-row and missing-index remain report-only; summary counts recompute to include appended rows
- [ ] regression tests seen RED first, including a custom-column-order table; mutation-checked; CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-05 | audit | Raised |
