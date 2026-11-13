# BG1416: help/verify.md's exit-3 row in the revert-check table leaves out git failing to read the base blob

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_help_exit3.py, changelog.d/BG1416.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: repair verifyfix, BG1009
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:13:43Z

## Summary

`_BaseUnreadable` also gives exit 3 but the table omits it.

## Steps to Reproduce

Read the row.

## Proposed Fix

Add the cause.

## Acceptance Criteria

- [ ] **AC1** Given help/verify.md, when its exit-3 row is read, then it names an unreadable base blob. Fails on: the omission.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_help_exit3.py::VerifyHelpExit3Tests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
