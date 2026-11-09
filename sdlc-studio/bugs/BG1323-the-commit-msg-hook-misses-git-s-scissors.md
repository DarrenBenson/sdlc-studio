# BG1323: The commit-msg hook misses git's scissors line under a non-default `core.commentChar`, the multi-id rule still reads trailers below it, and `_ledger_rows` and BG1264's fragment say an edited ledger row owns nothing

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, tools/tests/test_commit_msg_hook.py, changelog.d/BG1264.md, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
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

Read the comment character from git config in `_scissors_cut`, apply the cut before the multi-id rule reads trailers, and correct the docstring and fragment to say an added or edited row makes its unit an owner; pin each.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From the QA reviews of US1133 (round 2) and BG1264 (qa-seat-US1133-r1, qa-seat-BG1264-r1, non-blocking, 2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Read the comment character from git config in `_scissors_cut`, apply the cut before the multi-id rule reads trailers, and correct the docstring and fragment to...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
