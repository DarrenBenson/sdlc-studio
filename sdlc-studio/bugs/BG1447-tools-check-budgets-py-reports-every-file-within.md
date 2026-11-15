# BG1447: tools/check_budgets.py reports every file within budget while the pre-commit budgets lane fails the same tree on docgen drift

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/check_budgets.py, tools/tests/test_check_budgets_docgen.py, tools/tests/test_check_budgets.py, changelog.d/BG1447.md
> **Evidence:** Run twelve (RUN-01M7E52T) orchestrator friction log
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:37:41Z

## Summary

The pre-commit budgets lane runs `check_budgets` plus `docgen reading-guides --check` and `docgen surface --check`; a builder told to run tools/`check_budgets.py` sees 'All files within their budgets' and hands back a tree the hook refuses (US1152's land, run twelve).

## Steps to Reproduce

Add a heading to a reference page past 400 lines without regenerating its guide, run tools/`check_budgets.py` (passes), then commit (the budgets lane fails).

## Proposed Fix

Have `check_budgets.py` run the same docgen checks, or say in its output that the hook lane also checks generated docs.

## Acceptance Criteria

- [ ] **AC1** Given a reference page whose generated guide is stale, when tools/`check_budgets.py` runs, then it reports the drift or names the command that does. Fails on: a bare pass.
  - **Verify:** pytest tools/tests/test_check_budgets_docgen.py::CheckBudgetsDocgenTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
