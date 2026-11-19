# BG1332: No command writes a retro's 'Known issues carried' rows, so the orchestrator types them by hand and run nine's two late rows landed outside the table

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, changelog.d/BG1332.md
> **Evidence:** RETRO0142 before D0455; retro.py --help; a consuming project's agent, 2026-11-10
> **Created:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T17:25:03Z

## Summary

retro.py reads the 'Known issues carried' table (`KNOWN_ISSUES_SECTION`, read by the close's known-issues row) but no subcommand writes it: `retro.py --help` lists validate, dispose, extract, accuracy, velocity, estimator and collate. The orchestrator writes each row by hand from the open bugs raised during the run. In run nine, BG1327 and BG1328 were appended after the accuracy section instead of inside the table, so the report read them as unruled; fixing it took a reopen (D0455). A consuming project's agent asked on 2026-11-10 for this bookkeeping to be generated from the bug files, as `_index.md` already is by reconcile.

## Steps to Reproduce

1. Close a run that raised open bugs.
2. Look for a command that writes their rows into the retro's 'Known issues carried' table: there is none.
3. Append a row after the accuracy section by hand: the close's known-issues row reads it as unruled.

## Proposed Fix

Add `retro.py known-issues --write --retro RETROxxxx` that writes one row per open bug raised in the run (from each bug's Raised-in-batch), keeping any ruling already recorded and leaving new rows for the operator to rule, always inside the table.

## Acceptance Criteria

- [ ] **AC1** Given a run that raised two open bugs, and a retro whose accuracy section follows its 'Known issues carried' table, when `retro.py known-issues --write --retro <id>` is run, then one row per bug is inside the table and the close's known-issues reader returns both. Fails on: a row written after a later section, which the report reads as unruled.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::KnownIssuesWriteTests::test_one_row_per_open_bug_of_the_run_is_written_inside_the_table
- [ ] **AC2** Given a table that already holds one of those bugs with a ruling, when the command is run again, then that ruling is kept word for word, no row is doubled, and the new row is left for the operator to rule. Fails on: a recorded ruling overwritten, or a second run duplicating rows.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::KnownIssuesWriteTests::test_a_recorded_ruling_is_kept_and_a_second_run_adds_nothing
- [ ] **AC3** Given a bug of the run that is Fixed, and an open bug whose Raised-in-batch names another run, when the command is run, then neither gets a row. Fails on: a closed bug or another run's finding carried into this retro.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::KnownIssuesWriteTests::test_a_closed_bug_and_another_runs_bug_get_no_row

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Filed |
