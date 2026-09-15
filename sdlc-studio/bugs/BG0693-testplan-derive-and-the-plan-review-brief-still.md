# BG0693: testplan derive and the plan-review brief still name different unauthored sets: blank cells, table order and a criterion with no row

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0666-delivery-engineering.txt (engineering seat); verdicts/BG0666-delivery-qa.txt (qa seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The brief's note treats as unauthored only the exact placeholder (`testplan_unauthored`, `verify_ac.py`:3250), while the guard's own blank test treats an empty cell as blank (`testplan_row_faults`, `verify_ac.py`:3145), so the brief prints no note for an empty mutant cell or a re-spaced placeholder (probed); derive refuses both at exit 2, so only the brief stays silent. derive orders the ids by the declared criteria and the brief by table order, so an out-of-order table gives '(AC2, AC3)' from derive and '(AC3, AC2)' from the brief (probed). On a file where a criterion has no row, derive (including --dry-run) names it and the brief does not. The comment at critic.py:3515-3517 says the two surfaces cannot disagree about a plan; the helper docstring and changelog describe the difference, so only that comment over-claims. derive --dry-run prints the note (probed: exit 0, names AC2, AC3, AC4) but no test pins it: a mutant suppressing the note under --dry-run (`verify_ac.py`:3827-3829) survives all three Verify tests, and --dry-run is the exact command the originating bug's evidence quotes.

## Steps to Reproduce

1. In a fixture unit, leave one Test Plan mutant cell empty and write another as the placeholder with extra spaces. python3 .claude/skills/sdlc-studio/scripts/critic.py brief --unit <id> --seat qa --phase plan-review prints no unauthored note; python3 .claude/skills/sdlc-studio/scripts/`verify_ac.py` testplan derive --unit <id> exits 2. 2. Order the table with AC3 before AC2 - derive names (AC2, AC3), the brief (AC3, AC2). 3. Delete a criterion's row - derive names it, the brief does not.

## Proposed Fix

Give derive and the brief one helper that decides blankness as `testplan_row_faults` does, orders by the declared criteria and includes criteria with no row, and call it from both. Pin the --dry-run note. Correct the comment at critic.py:3515-3517 if any difference is kept.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The brief's note treats as unauthored only the exact placeholder (`testplan_unauthored`, `verify_ac.py`:3250), while the guard's own blank test treats an empty...
- [ ] **AC2** The proposed fix lands, pinned by a test: Give derive and the brief one helper that decides blankness as `testplan_row_faults` does, orders by the declared criteria and includes criteria with no row...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
