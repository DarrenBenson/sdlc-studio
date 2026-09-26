# BG0793: A boundary test lists changelog.d, which a fresh checkout does not have once a release cut consumes every fragment, so CI is red on the rc.1 commit

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py, changelog.d/BG0793.md
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T22:27:49Z

## Summary

`test_cli_grammar.py`::RealTreeMarkerTests::`test_the_control_is_green_in_either_fragment_state` calls (REPO / 'changelog.d').iterdir(). After the v6.0.0-rc.1 cut consumed every fragment (and the two post-cut fragments were composed), changelog.d holds no tracked file, git does not carry an empty directory, and CI's checkout has none: FileNotFoundError, CI Lint run 36273900516 red on 0abe99f6. The local tree keeps the empty directory, so the local release gate passed. Measured: it is the only test in the boundary suite that fails with changelog.d absent.

## Steps to Reproduce

rmdir changelog.d; `SDLC_STUDIO_BOUNDARY_SUITE`=1 python3 -m unittest `tests.test_cli_grammar.RealTreeMarkerTests` (from scripts/): FileNotFoundError.

## Proposed Fix

Read an absent changelog.d as no fragments in the test (and anywhere else it is listed), with a case that runs the control with the directory absent.

## Acceptance Criteria

- [ ] **AC1** Given a checkout with no `changelog.d/` directory (every fragment consumed by a release cut), when `test_cli_grammar.py::RealTreeMarkerTests` runs under the boundary suite, then it passes and reads the fragment state as empty. Fails on: listing `changelog.d` with `iterdir()` unguarded
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::RealTreeMarkerTests
  - **Verified:** yes (2026-09-26)
- [ ] **AC2** Given the same test run with `changelog.d/` absent, then a dedicated case proves the directory's absence is exercised, not skipped. Fails on: a fix that only passes because the directory happens to exist locally
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::RealTreeMarkerTests::test_the_control_holds_with_no_fragment_directory
  - **Verified:** yes (2026-09-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
