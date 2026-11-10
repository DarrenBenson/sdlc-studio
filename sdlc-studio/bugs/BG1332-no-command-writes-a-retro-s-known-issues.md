# BG1332: No command writes a retro's 'Known issues carried' rows, so the orchestrator types them by hand and run nine's two late rows landed outside the table

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
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

- [ ] **AC1** The behaviour described is corrected: retro.py reads the 'Known issues carried' table (`KNOWN_ISSUES_SECTION`, read by the close's known-issues row) but no subcommand writes it: `retro.py --help`...
- [ ] **AC2** The proposed fix lands, pinned by a test: Add `retro.py known-issues --write --retro RETROxxxx` that writes one row per open bug raised in the run (from each bug's Raised-in-batch), keeping any ruling...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Filed |
