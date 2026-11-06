# BG1254: sprint cost --anatomy reads the whole session, not the open run's window, so it cannot price one run inside a long-lived session

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** run seven (RUN-01M6RAP7) orchestrator, `sprint.py cost --anatomy` at 71b75bec
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T15:13:26Z

## Summary

Run on run seven's orchestrating session, `sprint.py cost --anatomy` reported 840.7M priced over 325 agents and 26,018 calls: every run the session ever held (runs five to seven), with 309 agents under other. CR0666 asked for the open run or a named one; US1124's criteria said the session. A run inside a session that spans runs is not separable, so the per-role table the report carries (US1123) is only right for a session opened with its run.

## Steps to Reproduce

In a session that held two runs, run `sprint.py cost --anatomy` and compare its total with the run's own meter delta on the report.

## Proposed Fix

Window the anatomy by the run's open and close timestamps (the meter already stamps both), counting only messages inside the window, and say so in the header; keep a `--session` flag for the whole-session view.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run on run seven's orchestrating session, `sprint.py cost --anatomy` reported 840.7M priced over 325 agents and 26,018 calls: every run the session ever held...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a session that held two runs, run `sprint.py cost --anatomy` and compare its total with the run's own meter delta on the report.
- [ ] **AC3** The proposed fix lands, pinned by a test: Window the anatomy by the run's open and close timestamps (the meter already stamps both), counting only messages inside the window, and say so in the header...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
