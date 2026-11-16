# BG1498: The push gate's noise check holds each module to its own budget, which CI's full run does not, so one leaked line in any of 16 modules at their budget refuses a push CI would pass; and its report counts modules that leaked nothing

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Affects:** tools/run-suite.sh, tools/tests/test_run_suite.py, changelog.d/BG1498.md, sdlc-studio/tsd.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) BG1493 QA verdict 52018e76dcb4-e6969996, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T05:52:24Z

## Summary

BG1493's QA seat approved it in run fifteen with two non-blocking notes. First, the push gate (tools/run-suite.sh --noise-gate) refuses a single module over its tools/test-noise-baseline.json entry, while GitHub CI's full run checks only `_total`; 16 of the 21 budgeted modules sit exactly at their entry and the run as a whole has 4 lines of headroom (100 of 104), so one new line in any of them refuses a push that CI would pass. AC1 was written that way, so it is not a defect in BG1493, but it can block pushes for a reason CI does not share. Second, the gate's report wording counts modules that leaked nothing (tools/run-suite.sh near line 222).

## Steps to Reproduce

Add one print to a passing test in a module at its budget, push: the gate refuses though CI's `_total` check would pass.

## Proposed Fix

Either have the push gate check `_total` only for a full run (as CI does), with per-module entries checked on a selected run, or lower the budgets as leaks are captured so modules are not at their ceiling; and count only modules that leaked in the report line.

## Acceptance Criteria

- [ ] **AC1** Given a full push-boundary run (no selection) whose passing suite leaks no more lines in total than `_total` in tools/test-noise-baseline.json, when `tools/run-suite.sh --noise-gate` judges it, then it passes even where one module is over its own entry, as CI's full-run check does; a run whose total is over `_total` is still refused, naming the modules that leaked. Fails on: a full run refused for a per-module overrun within `_total`.
  - **Verify:** pytest tools/tests/test_run_suite.py -k noise
  - **Verified:** yes (2026-11-16)
- [ ] **AC2** Given a selected run (a commit's module selection), when the noise gate judges it, then each selected module is still held to its own entry and the run to the sum over the selection, as tools/skill-tests.sh does. Fails on: a selected module over its entry passing.
  - **Verify:** pytest tools/tests/test_run_suite.py -k noise
  - **Verified:** yes (2026-11-16)
- [ ] **AC3** Given the gate's report, when it names leaking modules, then it counts only modules that leaked at least one line. Fails on: a count that includes modules with no leak.
  - **Verify:** pytest tools/tests/test_run_suite.py -k noise
  - **Verified:** yes (2026-11-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
