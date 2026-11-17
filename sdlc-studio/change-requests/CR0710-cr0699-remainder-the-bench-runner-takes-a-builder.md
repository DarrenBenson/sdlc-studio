# CR-0710: CR0699 remainder: the bench runner takes a builder-effort arm and reports priced tokens per point, review rounds and the held-back score per arm

> **Status:** In Progress
> **Decomposed-into:** EP0350
> **Priority:** Medium
> **Type:** Feature
> **Affects:** tools/bench/runner.py, tools/tests/test_bench_effort_arm.py, changelog.d/CR0710.md
> **Evidence:** Run fourteen groom (D0489): CR0699 split into A (US1165), B (US1166) and C, deferred.
> **Date:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T23:21:20Z

## Summary

CR0699 delivered its first part in run fourteen: the routing.effort setting, its plan stamp and lane-brief line (US1165) and each role's effort on the report (US1166). Its trial was deferred at refine: tools/bench/runner.py should run two arms that differ only in builder effort on the same fixture and report each arm's effort with its priced tokens per point, review rounds, rejections and held-back suite score. Before it is built the trial's keep rule must be recorded as a decision, and the claude CLI must be confirmed to take an effort flag (runner.py passes only --model today). Its second half is a measurement over a whole run, not a test. This request carries the remainder so CR0699 can be derived Complete.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Proposed Fix

Record the keep rule as a decision, confirm the CLI effort flag, then add the effort arm to tools/bench/runner.py with a test in the existing bench test module.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Raised |
