# BG1272: The pre-push check reads only the latest Lint run, so a push made while the previous run is still in progress never sees it fail

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .githooks/pre-push, tools/tests/test_pre_push_red_main.py
> **Evidence:** run eight (RUN-01M6RZQZ) mid-run push, GitHub Actions Lint run 42263229398
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:52Z

## Summary

The forge's Lint job failed on main at 8a00d2cc, fb93b20d and fd1c2b5b (BG1259) and the pre-push hook let each later push through, because every push left while the previous 45-minute run was still in progress; the hook reads the latest push-triggered run, and an unfinished one is not a red. The red was first read at run eight's mid-run push.

## Steps to Reproduce

Push, then push again within the CI run's duration while it is failing; the second push is not refused.

## Proposed Fix

When the latest run on main is in progress, read the most recent concluded run as well, or name the in-progress run and the parent commit it judges, so a red parent is never silently skipped.

## Acceptance Criteria

- [ ] **AC1** Given the newest push-triggered Lint run on main still in progress and the most recent concluded run a success, when the pre-push hook runs, then it names the in-progress run by id and the commit it judges, and says its result is not yet read. Fails on: an unfinished run over the parent commit passing in silence.
  - **Verify:** pytest tools/tests/test_pre_push_red_main.py::PrePushRedMainTests::test_an_in_progress_run_is_named_with_the_commit_it_judges
- [ ] **AC2** Given the newest run in progress and the most recent concluded run a failure nobody acknowledged, when the pre-push hook runs, then the push is refused naming the concluded run. Fails on: the in-progress run masking the red before it.
  - **Verify:** pytest tools/tests/test_pre_push_red_main.py::PrePushRedMainTests::test_a_red_concluded_run_behind_an_in_progress_one_refuses
- [ ] **AC3** Given no run in progress and the latest concluded run a success, when the pre-push hook runs, then it prints no in-progress line and does not refuse. Fails on: the new notice printed on every push.
  - **Verify:** pytest tools/tests/test_pre_push_red_main.py::PrePushRedMainTests::test_a_green_main_with_nothing_in_progress_says_nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
