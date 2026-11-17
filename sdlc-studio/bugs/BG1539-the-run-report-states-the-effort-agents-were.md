# BG1539: The run report states the effort agents were dispatched at, but a headless lane is never passed that effort

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
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

- [ ] **AC1** The behaviour described is corrected: The report of record states the reasoning effort each unit's builder and reviewer were dispatched at.
- [ ] **AC2** The proposed fix lands, pinned by a test: Make the claim true or make the report honest, in one change.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
