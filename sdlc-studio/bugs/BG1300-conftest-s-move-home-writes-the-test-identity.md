# BG1300: conftest's `_move_home` writes the test identity to whatever HOME names, overwriting, so a mutant that leaves HOME unmoved replaced the operator's ~/.gitconfig and 23 commits on main took the test author

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** conftest.py, .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py
> **Evidence:** ~/.gitconfig.sdlc-test-leak-2026-11-08 (68 bytes, mtime 13:30); `git log --format='%an' f43e2698^..f95e02aa` gives 23 commits by sdlc-studio tests
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T00:06:54Z

## Summary

`_move_home` (conftest.py:128-142) points HOME at the private directory and then writes `Path(os.environ["HOME"], ".gitconfig")` with `write_text`, which overwrites. When HOME was not moved, as under a mutant of `_move_home` or `PRIVATE_HOME` during BG1249's review, that line wrote `TEST_IDENTITY` ("sdlc-studio tests <tests@sdlc-studio.invalid>") over the operator's real ~/.gitconfig. Found during the 6.3.0 release on 2026-11-08: the file was written at 13:30:30, 41 s after the BG1249 reviewer built its scratch tree, and 23 commits on main, f43e2698 to f95e02aa, carry that author, and all of them are pushed. History was not rewritten, because recorded self-checks name those commits by sha. The reviewer's mutation run had nothing stopping it from writing outside its scratch tree.

## Steps to Reproduce

In a scratch copy of conftest.py, drop "HOME" from `PRIVATE_HOME`, set HOME to a temporary directory holding a `.gitconfig` with another identity, and run any pytest session: the file now holds `TEST_IDENTITY.`

## Proposed Fix

Write the identity to `Path(private, PRIVATE_HOME["HOME"], ".gitconfig")`, built from `private` and never from the environment, and refuse to replace a file that already exists there. Add a test that runs a session with HOME pointing at a temporary home holding a `.gitconfig` and asserts that file is byte-identical afterwards, including under the mutant above. Have `critic.py brief` tell a reviewer probing confinement code to run its mutants with HOME set to a temporary directory.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_move_home` (conftest.py:128-142) points HOME at the private directory and then writes `Path(os.environ["HOME"], ".gitconfig")` with `write_text`, which...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a scratch copy of conftest.py, drop "HOME" from `PRIVATE_HOME`, set HOME to a temporary directory holding a `.gitconfig` with another identity, and run any...
- [ ] **AC3** The proposed fix lands, pinned by a test: Write the identity to `Path(private, PRIVATE_HOME["HOME"], ".gitconfig")`, built from `private` and never from the environment, and refuse to replace a file...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
