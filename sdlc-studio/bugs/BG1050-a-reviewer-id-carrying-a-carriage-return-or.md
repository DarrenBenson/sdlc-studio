# BG1050: A reviewer id carrying a carriage return or line separator tears its own verdict row

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_clean_line_breaks.py, changelog.d/BG1050.md
> **Evidence:** BG1044 round-1 QA verdict in sdlc-studio/reviews/critic-verdicts.md, its [pre-existing] '_clean folds only the newline' item, executed at 692f867d and at 3109377d alike.
> **Created:** 2026-10-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-14T12:05:10Z

## Summary

`critic._clean` folds only '\n' when it writes a verdict row's cells. A reviewer id (or author, or issues text) carrying a carriage return, vertical tab, form feed or U+2028 is written raw, and the ledger is read back with universal newlines and splitlines, which break the row there. `read_verdicts` then warns 'malformed row' and skips it: the unit's rounds drop, a delivery verdict vanishes from every gate, and a ruling past the cap can read as not needed. The same holds at every commit since `_clean` was written; found by BG1044's QA seat outside that unit's diff.

## Steps to Reproduce

Record a delivery verdict with --reviewer $'qa\rseat', then `read_verdicts`: the row is reported malformed and skipped.

## Proposed Fix

Fold every character str.splitlines breaks on (\r, \x0b, \x0c, \x1c-\x1e, \x85, U+2028, U+2029) to a space in `_clean`, so every cell stays on its row.

## Acceptance Criteria

- [ ] **AC1** Given a delivery verdict whose reviewer id carries a carriage return, a form feed and U+2028, when it is recorded and the ledger read back, then the row reads whole with its reviewer folded to spaces.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_clean_line_breaks.py::CleanLineBreakTests::test_a_reviewer_id_with_every_splitlines_break_reads_back_whole

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-14 | sdlc-studio | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
