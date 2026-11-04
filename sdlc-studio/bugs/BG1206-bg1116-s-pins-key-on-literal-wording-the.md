# BG1206: BG1116's pins key on literal wording: the boundary-habit test refuses only gate.py, and the per-commit and AGENTS.md checks pass reworded regressions

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_agentic_lessons_full_suite.py, changelog.d/BG1206.md
> **Evidence:** BG1116 round-1 and round-2 verdicts, scratchpad run5/BG1116-verdict-r1.txt and -r2.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T13:39:46Z

## Summary

2026-11-04, BG1116's round-2 review (qa-seat-BG1116-r1, APPROVE, non-blocking). `test_the_boundary_habit_names_the_projects_own_test_command` refuses only `\bgate\.py\b` (tools/tests/`test_agentic_lessons_full_suite.py`:152), so a habit routing a consuming project's push through `/sdlc-studio gate --boundary push` passes, and help/gate.md:12 already offers that command. Round 1's second finding also stands: two leads telling the reader to run the full suite per commit pass `test_the_habit_runs_the_full_suite_at_the_boundary` (line 92), and 'on every commit beneath it' passes `test_agents_md_names_the_commit_each_ref_points_at` (lines 114-118).

## Steps to Reproduce

1. Append 'or with `/sdlc-studio gate --boundary push`' to the habit in reference-agentic-lessons.md.
2. `python3 -m pytest -q tools/tests/test_agentic_lessons_full_suite.py`: it passes.

## Proposed Fix

Refuse any route to the skill's own gate in the habit, and match the per-commit and every-commit shapes by meaning rather than one phrasing.

## Acceptance Criteria

- [ ] **AC1** Each of the reviewers' surviving rewordings fails a test in the module.
  - **Verify:** pytest tools/tests/test_agentic_lessons_full_suite.py

## Impact

A later edit can send consuming projects back to a gate that runs none of their tests, with the suite green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
