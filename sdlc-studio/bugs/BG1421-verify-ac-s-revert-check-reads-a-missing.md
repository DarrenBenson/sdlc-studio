# BG1421: verify_ac's revert check reads a missing runner binary as red rather than as no verdict

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_revert_check_missing_runner.py, changelog.d/BG1421.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: qa-seat-BG1009-r1 round 2 (pre-existing)
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:49:13Z

## Summary

When the runner a Verify line names (pytest, node) is not installed, the revert check reads the line red at both refs, as it did before this run's change; only a timeout counts as no verdict. A missing runner says nothing about the unit's change.

## Steps to Reproduce

Run `verify_ac`'s revert check on a unit whose Verify line names a runner absent from PATH.

## Proposed Fix

Tell a missing runner (the shell's 127 for the runner itself, not for a script it runs) from a red result.

## Acceptance Criteria

- [ ] **AC1** Given a Verify line whose runner binary is not on PATH, when the revert check runs it, then the line is reported as not judged, naming the missing runner, not as red. Fails on: a missing runner read as red.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_missing_runner.py::MissingRunnerTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
