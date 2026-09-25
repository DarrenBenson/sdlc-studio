# BG0764: BG0762's settle-fingerprint test calls git outside a confined environment, so the unconfined-git sweep is red

> **Status:** In Progress
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_settle_fingerprint.py
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`test_lean_settle_fingerprint.py` (BG0762, ea1a9ceb) runs raw git in its AC2 fixture. `test_gitutil.py`::UnconfinedRawGitCallSweepTests::`test_no_module_calls_git_without_a_confined_environment` now fails on {'`test_lean_settle_fingerprint`': (1, 0)} at main, so the push's full suite will refuse. Found by the US0927 review.

## Steps to Reproduce

python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/`test_gitutil.py`::UnconfinedRawGitCallSweepTests at main HEAD: fails naming `test_lean_settle_fingerprint.`

## Proposed Fix

Run the fixture's git through the confined helper the other test modules use (tests/gitutil), so the sweep counts it as confined; change no production code.

## Acceptance Criteria

- [ ] **AC1** Given main with this fix, when the unconfined-git sweep runs, then it passes and no longer names `test_lean_settle_fingerprint`; a fix that deletes the fixture's git steps instead of confining them fails AC2
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py::UnconfinedRawGitCallSweepTests
- [ ] **AC2** Given the settle fingerprint, then it still changes when a staged file's bytes are edited and holds while they are not, run through a confined git environment
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_settle_fingerprint.py::SettleFingerprintTests::test_the_fingerprint_still_changes_with_the_bytes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | Claude Opus 5.5 | Criteria authored with executable Verify lines for the Sprint 4 batch |
