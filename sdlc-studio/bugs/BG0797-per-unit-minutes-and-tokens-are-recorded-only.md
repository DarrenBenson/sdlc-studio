# BG0797: Per-unit minutes and tokens are recorded only on an In Progress transition the lean loop never makes, and the report does not say why the column is empty

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_unit_actuals.py, changelog.d/BG0797.md
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-27T07:29:13Z

## Summary

`run_state.record_unit_actual` opens a unit's span only on a move to In Progress and closes it at a terminal status. Sprint 5's units went from Draft straight to Done at landing, so all 37 read NOT MEASURED - not recorded, and the report gives no reason or remedy; the estimate-accuracy promise (points, time and tokens per unit) is unmet for every lean run.

## Steps to Reproduce

RPT0010 per-unit table: 37 of 37 NOT MEASURED - not recorded; sdlc-studio/.local/run-state.json has no `unit_actuals` entries.

## Proposed Fix

Open a unit's span when its build is dispatched or its first verify or verdict is recorded (a lean-loop event that always happens), keep In Progress as one trigger, and have the report name the cause when no span was recorded.

## Acceptance Criteria

- [ ] **AC1** Given an open run and two delegated totals recorded with `retro.py accuracy --delegated-tokens N --delegated-unit US0001 --delegated-minutes M`, when the report derives, then US0001's row reads the sum of their tokens and minutes, labelled agent tokens and agent minutes. Fails on: HEAD reading only In Progress spans, so all 37 of RPT0010's units read NOT MEASURED, or a span on the shared main-thread meter, which counts the other parallel units' traffic
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_unit_actuals.py::UnitActualsTests::test_a_unit_s_tagged_delegated_totals_are_its_actuals
- [ ] **AC2** Given tagged and untagged delegated totals, when the run's token total is derived, then each record counts once. Fails on: adding the per-unit sums to the run total beside the records they came from
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_unit_actuals.py::UnitActualsTests::test_tagged_totals_count_once_in_the_run_total
- [ ] **AC3** Given a batch unit with no span and no tagged total, when the report derives, then its row reads NOT MEASURED naming both missing sources and the `--delegated-unit` flag. Fails on: the bare 'not recorded' RPT0010 prints
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_unit_actuals.py::UnitActualsTests::test_an_unmeasured_unit_names_why

## Notes

- Sprint 6 engineering: attribute delegated agent totals to units rather than opening spans at the first verdict; the loop runs 4-7 agents at once, so a span on the main-thread meter cannot say which unit spent what. The data is already recorded in free text: 69 of RUN-01M3CK1K's 73 delegated records name their unit in the note (13,121,230 tokens over 36 units); the new field makes it structured. The Agent tool reports tokens and duration, so minutes come from the same record. Keep the In Progress span as it is. `critic.py` leaves Affects: no verdict-time hook is needed. Does not have to precede BG0798's tokens-per-point fix; it must precede any minutes-per-point re-fit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | Groomed for Sprint 6: per-unit actuals from tagged delegated totals, not main-thread spans; critic.py dropped from Affects |
