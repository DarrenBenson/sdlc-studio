# BG0913: Each re-close moves the run's window end and token meter, so work after the first close counts as run cost

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_reclose_keeps_window.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RUN-01M3Y7DP re-closes for BG0911 (RPT0015 2bf8c07d -> bf505c4e)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T21:37:43Z

## Summary

sprint close re-run on a closed run refiles the page with its window ended at the re-close moment, so the main-thread token meter and the wall-clock span keep growing with every correction made after the first close. RUN-01M3Y7DP's main-thread tokens read 0.64M at the first close and 3.47M after four re-closes (window 3.4h to 5.3h), so the signed RPT0015 counts the orchestrator's post-close paperwork as the run's cost.

## Steps to Reproduce

1. sprint close a run (page A). 2. Do an hour of unrelated work in the same session. 3. sprint close --retro again -> page B's window end, Minutes and Tokens actuals all moved forward.

## Proposed Fix

Keep the window end and meter reading of the first successful close on the run record and re-derive a re-close's page against them, so only artefact changes move a re-filed page.

## Acceptance Criteria

- [ ] **AC1** Given a run closed once at T with a main-thread meter reading M, when it is re-closed at T plus one hour after more session work, then the re-filed page's window end is T and its main-thread tokens read M. Fails on: the current code moves both to the re-close
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_reclose_keeps_window.py::RecloseKeepsWindowTests::test_a_re_close_keeps_the_first_close_s_window_and_meter

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
