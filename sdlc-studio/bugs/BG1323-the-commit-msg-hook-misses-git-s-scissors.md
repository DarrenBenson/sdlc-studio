# BG1323: The commit-msg hook misses git's scissors line under a non-default `core.commentChar`, the multi-id rule still reads trailers below it, and `_ledger_rows` and BG1264's fragment say an edited ledger row owns nothing

> **Status:** Fixed
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, tools/tests/test_commit_msg_hook.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py, changelog.d/BG1323.md
> **Evidence:** US1133-verdict-r2 and BG1264-verdict-r1 (RUN-01M7061X)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T17:42:39Z

## Summary

From the QA reviews of US1133 (round 2) and BG1264 (qa-seat-US1133-r1, qa-seat-BG1264-r1, non-blocking, 2026-11-09). (1) `_scissors_cut` finds git's scissors line only for the default `#` comment character, so with `core.commentChar` set otherwise a `git commit -v` diff below it is read. (2) The multi-id rule still reads trailers from below the scissors line. (3) The `_ledger_rows` docstring and changelog.d/BG1264.md say an existing ledger row makes no unit an owner, but an edited row does. BG1263 (Refs read below the scissors) stays Open although US1133's change does what its proposed fix asks; it needs its own review before it can be Fixed.

## Steps to Reproduce

1. In a scratch clone set `core.commentChar` to `;` and commit with `git commit -v` naming two ids: the hook reads the diff below the scissors.
2. Edit an existing row of critic-verdicts.md in a commit: its unit is treated as an owner, contrary to the docstring and fragment.

## Proposed Fix

Read the comment character from git config in `_scissors_cut`, apply the cut before the multi-id rule reads trailers, and correct the docstring (the BG1264 fragment no longer exists: it was folded into the 6.4 notes, which stay as released) to say an added or edited row makes its unit an owner; pin each.

## Acceptance Criteria

- [ ] **AC1** Given a clone with `core.commentChar` set to `;`, when the commit-msg hook runs on a verbose message naming two ids, then the hook reads nothing below git's scissors line and writes its trailers above it. Fails on: `_SCISSORS_RE` (`^# -+ >8 -+$`) never matching `; ---- >8 ----`: `_scissors_cut` returned the line count, i.e. no cut (reproduced at HEAD).
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::DerivedTrailerTests::test_the_scissors_line_is_found_under_a_non_default_comment_character
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given a verbose message whose subject names two ids and whose diff below the scissors line carries a `Refs:` diff context line naming both, when `check_commit_message` judges it, then it warns that the ids lack a trailer. Fails on: `check_commit_message` reading the whole message, so a trailer in git's diff satisfies the rule (reproduced at HEAD: returns `(0, None)`).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CommitMsgCheckTests::test_a_refs_line_below_the_scissors_accounts_for_no_subject_id
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given a commit editing one existing `critic-verdicts.md` row and leaving another untouched, when `_ledger_rows` is read, then the edited row's unit owns the ledger and the untouched row's unit does not, and its docstring says an added or edited row owns. Fails on: the docstring saying only an added row counts while an edited row (a `+` line in the -U0 diff) owns.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::RefsTrailerAttributionTests::test_an_edited_ledger_row_owns_and_an_untouched_one_does_not
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: Points 2 to 3 (the hook test needs a real clone and the `check_commit_message` leg is a second code path); Affects gains changelog.d/BG1323.md; criteria name the observed failures; scissors cut under `#` is already applied by `derive_trailers`, only `check_commit_message` and the non-default character remain |
