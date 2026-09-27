# BG0796: The report's cost row reads unattributed while the same report measures the run's tokens

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_cost_row.py, changelog.d/BG0796.md
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-27T07:29:12Z

## Summary

RPT0010's Estimates table measures 19.2M tokens from the run record (main thread plus 73 delegated agents), but the checklist's cost row reads 'not measured - no per-unit telemetry and no harness-tracked sprint total', because `_ck_cost` reads only per-unit spans and `sprint_actual_tokens`, which is set only by a hand-supplied retro.py accuracy --tokens. Two readers of one fact disagree, and the Not measured appendix states something false.

## Steps to Reproduce

`sprint_report.py` render --report RPT0010: Estimates tokens 19,225,437; Not measured: cost 'no harness-tracked sprint total'.

## Proposed Fix

Read the run's measured token total (`run_state.run_token_total`, as the Estimates section does) in `_ck_cost` and in retro accuracy, so a hand --tokens is an override, not the only source; one reader for the figure.

## Acceptance Criteria

- [ ] **AC1** Given a run whose record carries token stamps and delegated totals and no hand `--tokens`, when the checklist composes, then the cost row is answered with the run's measured total, the same figure the Estimates section states. Fails on: HEAD's `_ck_cost`, which answers 'unattributed' unless `sprint_actual_tokens` was supplied by hand (RPT0010: Estimates 19,225,437; cost 'no harness-tracked sprint total')
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_cost_row.py::CostRowTests::test_the_cost_row_reads_the_run_s_measured_total
- [ ] **AC2** Given the same run and `retro.py accuracy --tokens N`, when the checklist composes, then the cost row states N and names it supplied. Fails on: the measured total silently replacing an operator's override
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_cost_row.py::CostRowTests::test_a_supplied_total_overrides_and_is_named

## Notes

- Sprint 6 engineering: one reader, `run_state.run_token_total`, as the Estimates section uses. Note RPT0010's Estimates (19,225,437) and RETRO0125's VELOCITY row (18,791,718) are two moments of one growing total; AC1 pins the cost row to the Estimates figure only.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | Groomed for Sprint 6: criteria and Verify selectors written |
