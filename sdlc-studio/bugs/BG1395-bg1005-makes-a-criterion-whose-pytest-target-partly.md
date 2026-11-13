# BG1395: BG1005 makes a criterion whose pytest target partly skips on the running machine read red, including Done criteria the release gate re-runs, and the count is not measured

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_partial_skip.py, .claude/skills/sdlc-studio/scripts/tests/test_partial_skip_release_gate_count.py, changelog.d/BG1395.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane verify builder, BG1005
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:10:53Z

## Summary

`verify_ac` now fails any criterion whose pytest target partly skips (`verify_ac.py` around line 463). Done criteria that skip on the release machine will read red at the gate; how many is not measured.

## Steps to Reproduce

Run `verify_ac` over Done stories and count partial skips.

## Proposed Fix

Measure before the next release; allow an explicit skip allowance if needed.

## Acceptance Criteria

- [ ] **AC1** Given the Done stories' Verify lines, when they are run on the release gate host, then the number that read red from a partial skip is counted and reported before the release. Fails on: no measurement.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_partial_skip_release_gate_count.py::PartialSkipReleaseGateCountTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
