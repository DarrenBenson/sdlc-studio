# BG1284: Dollars per point omits the coverage its dollar figure has, and the Priced cost row's reach sentence uses Claude-transcript wording for every harness

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG1284.md
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg A; repro under scratchpad rel63/legs/scratch-a/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:07:25Z

## Summary

Dollars per point divides a dollar figure that may cover only part of the priced tokens, but its basis omits the coverage the Dollar cost row states. Separately, the Priced cost row's reach sentence is Claude-transcript wording ('a subagent's transcript was not read') even when Copilot, OpenCode, Codex or Cursor metered the run.

## Steps to Reproduce

by reading.

## Proposed Fix

Append `_usd_reach(got)` to the Dollars per point basis. Phrase the Priced cost reach from `_meters_named(run_tokens)` when another harness metered the run.

## Acceptance Criteria

- [ ] **AC1** Given a closed run in which two models spent and the price table lists only one, when the sprint report renders its Estimates, then the Dollars per point basis carries the same coverage clause as the Dollar cost row: the share of the priced tokens it covers and the model left unpriced. Fails on: a per-point figure that reads as covering every priced token when its dollars cover part of them.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_dollars_per_point_states_the_coverage_its_dollar_figure_has
- [ ] **AC2** Given a run a harness other than Claude metered (a Codex reading), when the report renders the Priced cost row, then its reach is phrased from that harness's meter and does not say a subagent's transcript was not read, while a run Claude alone metered keeps the wording it has. Fails on: Claude-transcript wording on a Copilot, OpenCode, Codex or Cursor run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_the_priced_cost_reach_names_the_harness_that_metered_the_run

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. Basis and reach sentence wording on the dollar report.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
