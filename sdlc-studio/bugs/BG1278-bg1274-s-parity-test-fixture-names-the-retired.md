# BG1278: BG1274's parity-test fixture names the retired module audit.py, so the push gate's rename guard is red

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py (the rename guard, read by AC1 and unchanged)
> **Evidence:** run eight (RUN-01M6RZQZ) close push of bca8b1e6, refused at the push boundary by devserver1's full suite
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T22:48:36Z

## Summary

The push of bca8b1e6 was refused by the full suite on devserver1: `test_readiness.py::RenameTests::test_no_shipped_file_references_the_old_module_names` and `RenameDocsTests` name `scripts/tests/test_engagement_floor.py`, whose parity test (added by BG1274, ffe55071) uses `tool/audit.py` as a fixture path and quotes CR0155's `scripts/audit.py` declaration in a comment. The per-commit run selected no readiness test for the change, so only the push caught it.

## Steps to Reproduce

Run `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py -q -k Rename` at bca8b1e6.

## Proposed Fix

Use a neutral fixture name in place of `audit.py` in the parity test and its comment, keeping the bracketed-note-with-a-comma shape the test pins.

## Acceptance Criteria

- [ ] **AC1** No shipped file names a retired module: the rename guard's two tests pass.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::RenameTests .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::RenameDocsTests
  - **Verified:** yes (2026-11-06)
- [ ] **AC2** The parity test still pins the bracketed-note-with-a-comma declaration shape, and every test in its module passes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Criteria authored for run eight |
