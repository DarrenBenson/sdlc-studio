# BG1033: When sign cannot read the close's carried rows it moves every unit, and the warning it prints has no test

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_unreadable_carried_rows.py, changelog.d/BG1033.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T10:00:08Z

## Summary

Found by BG1025's round-2 QA review on 2026-10-13 (APPROVE, non-blocking). `_seal_units` prints `sign: the carried known issues could not be read (<why>) - no unit is held back as carried` when `_carried_rulings` names a reason (sprint.py, the BG1025 repair), and then moves every non-terminal unit, a carried one included: the branch fails open. With `_filed_retro` forced to a missing id, BG0101 is moved to Fixed after that line. No test covers the line or the outcome; deleting it passes every test. The reviewer judged it unreachable through the CLI today, because removing the close's retro changes the tree and sign refuses first.

## Steps to Reproduce

Patch `sprint._filed_retro` to return a retro id that does not exist, close and sign the BG1025 fixture run: sign prints the could-not-be-read line and moves the carried BG0101 to Fixed.

## Proposed Fix

Decide the branch (refuse to seal while the carried rows the page names cannot be read, or keep moving and say so) and pin whichever ships with a test that fails when the line or the outcome changes.

## Acceptance Criteria

- [ ] **AC1** Given a run whose filed page names a retro sign cannot read, when `sprint sign` runs, then it says why on stderr and the outcome for a unit that retro would carry is the one the fix decides, pinned by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_unreadable_carried_rows.py::SignUnreadableCarriedRowsTests::test_unreadable_carried_rows_are_named_and_decided

## Impact

Low: unreachable through the CLI today; if a later change makes it reachable, a carried unit would be moved with only a stderr line saying so.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
