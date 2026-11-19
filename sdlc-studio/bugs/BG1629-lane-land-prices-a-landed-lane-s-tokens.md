# BG1629: lane land prices a landed lane's tokens from the agent transcript but records no minutes, so every unit with a repair round reads minutes NOT MEASURED in the report

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1629.md
> **Evidence:** run eighteen, 2026-11-19: sdlc-studio/reports/RPT0037-sprint-report-run-01m7ss62.md Estimates table
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T19:53:17Z

## Summary

Run eighteen's report (RPT0037) shows minutes NOT MEASURED for the seven units that had a repair round (US1192, US1196, US1197, US1198, US1201, US1202, US1238): '0 of its 2 tagged agent(s) reported minutes ... recorded with its --delegated-tokens as --delegated-minutes M when it reports, and cannot be added afterwards'. lane land prices each unit's return from the builder's transcript, split by points, but records no minutes, although the same transcript carries the agent's start and end. A unit built once is measured over its own open span instead, so only the units that went through repair lose their minutes, which are the ones a cost-per-unit run most needs to see.

## Steps to Reproduce

Land a unit, REJECT it, land its repair with lane land, close the run: the unit's Minutes cell reads NOT MEASURED.

## Proposed Fix

Have lane land record --delegated-minutes from the transcript's first and last message times beside the tokens it prices, split by points as the tokens are.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run eighteen's report (RPT0037) shows minutes NOT MEASURED for the seven units that had a repair round (US1192, US1196, US1197, US1198, US1201, US1202...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Land a unit, REJECT it, land its repair with lane land, close the run: the unit's Minutes cell reads NOT MEASURED.
- [ ] **AC3** The proposed fix lands, pinned by a test: Have lane land record --delegated-minutes from the transcript's first and last message times beside the tokens it prices, split by points as the tokens are.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
