# BG1254: sprint cost --anatomy reads the whole session, not the open run's window, so it cannot price one run inside a long-lived session

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, changelog.d/BG1254.md
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

- [ ] **AC1** Given a session transcript, with subagent transcripts, holding messages before the open run's `started_at` and messages inside the run, when `sprint.py cost --anatomy` runs, then only messages timestamped inside the run's window are counted, per role and in the total, and the header names the window. Fails on: `build` counting every record regardless of its timestamp.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_the_anatomy_is_windowed_to_the_open_run
  - **Verified:** yes (2026-11-06)
- [ ] **AC2** Given the same session and `sprint.py cost --anatomy --session`, then every message is counted and the header says the whole session was read. Fails on: `--session` ignored, so the window still applies.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_the_session_flag_reads_the_whole_session
  - **Verified:** yes (2026-11-06)
- [ ] **AC3** Given no open run, when `sprint.py cost --anatomy` runs, then it reads the whole session and says no run is open, never an empty table read as zero spend. Fails on: a window with no start defaulting to nothing, which prints a zero anatomy.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_with_no_open_run_the_session_is_named_not_zeroed
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria with Verify checks, Points and Affects |
