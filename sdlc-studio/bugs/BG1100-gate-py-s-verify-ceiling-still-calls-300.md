# BG1100: gate.py's verify ceiling still calls 300 s CI's figure, though corpus-verify now runs every criterion under 450 s

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_release_verify_ceiling.py, changelog.d/BG1100.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** lint.yml run 39322298831 (2026-10-19): 'verifier-time: US0940::AC1 353 s'. BG1054 part two sets SDLC_VERIFY_TIMEOUT: 450. gate.py VERIFY_TIMEOUT = 300.
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-20T07:06:53Z

## Summary

gate.py's `VERIFY_TIMEOUT` comment says the release verify lane's 300 s default is 'CI's figure', so that a release gate on a developer machine never reads red what CI reads green. BG1054 raised the corpus-verify job's `SDLC_VERIFY_TIMEOUT` to 450 s after run 39322298831 measured US0940 AC1 at 353 s on the runner. The comment is now false, and `test_lean_release_verify_ceiling.py` pins the old 300.

## Steps to Reproduce

Compare gate.py `VERIFY_TIMEOUT` (300, 'CI's figure') with .github/workflows/lint.yml corpus-verify `SDLC_VERIFY_TIMEOUT` (450).

## Proposed Fix

Read the default from the workflow's figure, or set it to 450 and pin the two equal in a test that reads both.

## Acceptance Criteria

- [ ] **AC1** gate.py's default verify ceiling equals the corpus-verify job's, read from the workflow
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_release_verify_ceiling_ci.py::ReleaseVerifyCeilingCiTests

## Impact

A slow developer machine reads red at release what CI reads green, the drift the default was set to prevent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | Claude Opus 5.5 | Filed |
