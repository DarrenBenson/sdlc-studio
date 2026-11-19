# BG1539: The run report states the effort agents were dispatched at, but a headless lane is never passed that effort

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG1539.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, stories lens, survived 3 of 3 refute votes; observed at sdlc-studio/stories/US1166-each-run-s-report-of-record-states-the.md AC1 and AC3 (with US1165 Notes line on headless lanes); .claude/skills/sdlc-studio/scripts/sprint_report.py:4534 _dispatch_effort; scripts/lib/lanes.py:629 headless_command
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:00Z

## Summary

The report of record states the reasoning effort each unit's builder and reviewer were dispatched at. `_dispatch_effort` in `sprint_report.py` (line 4534) derives that figure by counting the effort stamp `sprint plan` wrote on each plan row, and `reference-evidence-schema.md` (line 215) and `reference-config.md` (line 479) describe it as the effort the agents were spawned at. `headless_command` in `lib/lanes.py` (lines 629 to 654) builds the command for a headless lane with a model flag only and no effort flag, because US1165 ruled headless lanes out of scope. A project that sets `routing.effort` with builder low and runs its lanes headless therefore gets a signed report stating builder low for agents that ran at the harness default. No criterion in US1165 or US1166 covers the configured-but-not-applied case, and no page says a headless lane ignores the setting. The report presents the intent as the fact (LL0008, LL0016).

## Steps to Reproduce

1. In a fixture project, set `routing.effort.builder` to low in the configuration and run `sprint plan`, so each plan row is stamped with that effort.
2. Read `headless_command` in `.claude/skills/sdlc-studio/scripts/lib/lanes.py` (lines 629 to 654), or call it for any harness: the returned command carries a model flag at most and no effort flag. A search of `lanes.py` for the word effort finds nothing.
3. Run the lane headless with `sprint lane run` and `--harness`, close the run and read the cost section of the report.
4. Observe the Effort line stating builder low for the units, described as the effort the agents were dispatched at.
5. Expected: the report states the effort the agents ran at, or says the setting was configured and not applied to headless lanes. Actual: it reports the configured value as the dispatched one.

## Proposed Fix

Make the claim true or make the report honest, in one change. Either extend `headless_command` in `lib/lanes.py` to pass the stamped effort to each harness whose command line accepts one, and record on the lane row what was passed; or leave headless lanes as they are and have `_dispatch_effort` in `sprint_report.py` report a headless unit's effort as configured and not applied, with the reason. In both cases reword `reference-evidence-schema.md`, `reference-config.md` and `reference-sprint.md` so they say what a headless lane does with `routing.effort`. Add a test to `test_lane_run.py` for the command each harness receives, and one to `test_report_effort.py` that a headless unit's effort line never reads as dispatched when no effort was passed.

## Acceptance Criteria

- [ ] **AC1** Given a project with `routing.effort.builder` set to low and a run whose lane ran headless on a command that carried no effort flag, when the report of record is written, then that unit's Effort line does not read as dispatched at low: it says the effort was configured and not applied, with the reason, unless the command did carry it. Fails on: the configured value reported as the effort the agent ran at.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py::ReportEffortTests::test_a_headless_unit_is_never_reported_dispatched_at_an_effort_not_passed
- [ ] **AC2** Given each harness `headless_command` supports and a plan row stamped with an effort, when the lane command is built and the lane row is recorded, then the row records exactly the effort the command carried: the flag and the record together, or neither. Fails on: a lane row recording an effort the command line does not carry, or a flag passed to a harness that does not accept one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::HeadlessEffortTests::test_the_lane_row_records_the_effort_the_command_carried
- [ ] **AC3** Given a unit dispatched in session at the stamped effort, when the report is written, then its Effort line still reads as dispatched at that effort. Fails on: the correction for headless lanes degrading the line for a unit whose effort was applied.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py::ReportEffortTests::test_an_in_session_unit_still_reads_as_dispatched
- [ ] **AC4** Given `reference-evidence-schema.md`, `reference-config.md` and `reference-sprint.md`, when their accounts of `routing.effort` are read, then each says what a headless lane does with the setting and none describes the reported figure as the effort every agent was spawned at. Fails on: a page still presenting the stamped intent as the fact for a headless lane.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py::ReportEffortDocsTests::test_the_three_pages_say_what_a_headless_lane_does_with_effort

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
