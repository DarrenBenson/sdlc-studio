# BG1119: Two behaviours BG1000's repair states for per-commit selection are pinned loosely or not at all: the census header's 40-line window, and the rewritten run reason

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_census_window.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_selection_reaches_loaders.py, changelog.d/BG1119.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** BG1000 QA review round 2, qa-seat-BG1000-r1, 2026-10-22, at a5550c96: new findings 1 and 2.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T12:10:18Z

## Summary

BG1000's round-2 QA review (APPROVE, 2026-10-22). (1) gate.py now reads a test module's first census marker within its first 40 lines (`_CENSUS_HEAD_LINES`), matching tools/`test_census.py`; the fixtures' markers sit on lines 33 and 54, so a window of 35, 50 or 53 passes every test, and changelog.d/BG1000.md's 'first 40 lines' is held only to within lines 33-53. No real marker sits past line 29, so no selection changes today. (2) The run reason the repair rewrote (gate.py:2415-2419, 'N of M selected for the K changed file(s): each is one of them, or ...') is true when run but no test reads it.

## Steps to Reproduce

Set `_CENSUS_HEAD_LINES` to 50 and run tests/`test_gate_selection_reaches_loaders.py`: green. Revert the run reason to its earlier text: green.

## Proposed Fix

Fixtures with markers on lines 40 and 41 (the boundary), and one assertion on the run reason's text for a staged test module and a staged script.

## Acceptance Criteria

- [ ] **AC1** Given a census marker on line 40 and another module's on line 41, then selection reaches the first and not the second
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_census_window.py::CensusWindowTests::test_the_window_ends_at_line_forty
- [ ] **AC2** Given a staged test module and a staged script, then the run reason names each as the selection states it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_census_window.py::CensusWindowTests::test_the_run_reason_says_why_each_module_runs

## Impact

Either behaviour can drift with the suite green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
