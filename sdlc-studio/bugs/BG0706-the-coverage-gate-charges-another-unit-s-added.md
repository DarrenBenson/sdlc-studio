# BG0706: The coverage gate charges another unit's added lines to a unit sharing its file, and a coverage ruling is voided by any edit to that file

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** findings/todo.txt, RUN-01M2JA6J 2026-09-15: 'coverage gate attributes every added line in a shared Affects file to each unit (BG0674 refused Fixed on 455 US0626 lines in sprint.py)' and 'coverage rulings are bound to the whole-file hash ... (BG0659/BG0672 re-ruled after BG0677 touched critic.py/`test_critic.py)`'; commit 68bd3c13 records the per-unit attribution read after the split. Mechanism read at HEAD in `verify_ac.py` `_unit_commit_shas`, `_unit_added_lines` and `live_rulings`. The mutant-row counterpart is CR0570.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_unit_added_lines` (`verify_ac.py`:2188) counts a line as the unit's when git blame puts it on a commit whose subject or Refs line names the unit, or leaves it uncommitted. In an Affects file several batch units share, another unit's uncommitted lines and every line of a commit naming more than one unit are charged to each unit: BG0674 was refused Fixed on 455 lines of US0626's work in sprint.py, and the run had to split commits per unit before the gate read true attribution. A coverage ruling is keyed on the whole file's content hash (`live_rulings`, `verify_ac.py`:2413), so another unit's edit anywhere in the file voids it: BG0659's and BG0672's rulings had to be made again after BG0677 touched critic.py and `test_critic.py.`

## Steps to Reproduce

1. With two units sharing sprint.py, leave unit A's added lines uncommitted and run python3 .claude/skills/sdlc-studio/scripts/`verify_ac.py` run --coverage --id <unit B> - unit B is charged with A's lines. 2. Record a coverage ruling for unit B on a line of critic.py, then change an unrelated line of critic.py for unit C - unit B's ruling now reads stale.

## Proposed Fix

Attribute uncommitted lines only to the unit being delivered when the run can tell, and split a multi-unit commit's lines by each unit's declared hunks or refuse to guess and say so. Key a ruling on the ruled line's own content and neighbourhood, as the whole-file mutation-ledger change proposes for mutant rows, rather than on the whole file's hash.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_unit_added_lines` (`verify_ac.py`:2188) counts a line as the unit's when git blame puts it on a commit whose subject or Refs line names the unit, or leaves...
- [ ] **AC2** The proposed fix lands, pinned by a test: Attribute uncommitted lines only to the unit being delivered when the run can tell, and split a multi-unit commit's lines by each unit's declared hunks or...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
