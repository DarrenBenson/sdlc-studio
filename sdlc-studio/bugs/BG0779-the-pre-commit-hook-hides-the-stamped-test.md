# BG0779: The pre-commit hook hides the stamped-test re-read list on a passing commit

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .githooks/pre-commit, tools/tests/test_pre_commit_hook.py
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T18:44:42Z

## Summary

US0945 makes `verify_ac` `staged_stamps` list every stamped criterion whose test the commit changes (advisory, exit 0). .githooks/pre-commit's verdict() prints a lane's output only on FAIL, so on a passing commit the list is never shown, and the advisory reaches the author only when the commit is already refused for an orphan. Found by US0945's builder.

## Steps to Reproduce

1. Stage an edit to a test node a Verified: yes criterion names. 2. git commit. 3. The stamps-staged lane prints ok and no re-read list.

## Proposed Fix

Print the stamps-staged lane's output on success when it carries a re-read block (advisory only, no new refusal), with a hook test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US0945 makes `verify_ac` `staged_stamps` list every stamped criterion whose test the commit changes (advisory, exit 0).
- [ ] **AC2** The proposed fix lands, pinned by a test: Print the stamps-staged lane's output on success when it carries a re-read block (advisory only, no new refusal), with a hook test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
