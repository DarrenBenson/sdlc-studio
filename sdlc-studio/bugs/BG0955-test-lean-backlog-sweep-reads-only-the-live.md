# BG0955: test_lean_backlog_sweep reads only the live _index.md, so the v6.1 row archive turned main red with 25 false disagreements

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py
> **Evidence:** Lint run 37335339814 on aa19a2e3 (and the 2c72fe8e push and schedule runs): ci job, 25 failures in test_lean_backlog_sweep; reproduced locally 2026-10-06 against cdfd994d.
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T16:43:19Z

## Summary

`test_the_due_holds_are_closed` asserts each due hold's index row agrees with its file through `_index_status` (`test_lean_backlog_sweep.py`:145), which reads only `<type>/_index.md`. Commit 2c72fe8e archived 747 terminal rows into `<type>/archive/<release>/*.md` sub-indexes, so every archived hold reads as '' against its file's status and the test fails 25 times. Main's Lint has been red since that push (runs for 2c72fe8e and aa19a2e3), and the pre-push gate refuses every push until it is fixed. The archive is correct: reconcile's census already unions archive rows with the live table, live winning (reconcile.py:374), and detect reports 0 drift. The defect is the test helper.

## Steps to Reproduce

From .claude/skills/sdlc-studio/scripts: python3 -m unittest `tests.test_lean_backlog_sweep` -> FAILED (failures=25), each `AssertionError: '' != 'Superseded'` naming an archived id (BG0679, CR0543, US0682 ...). Lint run 37335339814 shows the same 25.

## Proposed Fix

Have `_index_status` read the live `_index.md` first and then the `archive/**` sub-indexes, matching the rebased `../../<file>` links archive rows carry, the live row winning - the union reconcile's census takes. Do not skip archived items: an archived row that disagrees with its file must still fail.

## Acceptance Criteria

- [ ] **AC1** With the v6.1 archive in place, every due hold's index row, live or archived, agrees with its file and `test_the_due_holds_are_closed` passes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_the_due_holds_are_closed
  - **Verified:** yes (2026-10-06)
- [ ] **AC2** An artefact whose row sits only in an `archive/**` sub-index is read with that row's Status, so an archived row that disagrees with its file still fails
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::IndexStatusReaderTests::test_an_archived_row_is_read
  - **Verified:** yes (2026-10-06)
- [ ] **AC3** A live row wins over an archived row for the same artefact
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::IndexStatusReaderTests::test_a_live_row_wins_over_an_archived_one
  - **Verified:** yes (2026-10-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Filed |
