# US0875: The sprint report is one page answering three questions, with everything else in an appendix

> **Status:** Done
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py
> **Epic:** EP0260
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** operator signing off a sprint
**I want** a one-page report that answers how accurate the estimates were, whether we delivered to plan, and what known issues are handed over
**So that** sign-off is quick and the answers are the ones I need

## Acceptance Criteria

- **AC1:** Given a closed run, when the report is built, then its front page has exactly five sections in order: Goal, Estimates, Delivered to plan, Known issues handed over, Sign-off
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py::OnePageTests::test_the_front_page_has_exactly_the_five_sections
  - **Verified:** yes (2026-09-23)
- **AC2:** Given a `plan_snapshot` and `unit_actuals` in run state, then Estimates shows points, minutes and tokens as forecast, actual and ratio, and planned points come from the snapshot so a unit resized from 3 to 8 shows planned 3 and actual 8
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py::OnePageTests::test_estimates_read_the_plan_snapshot_and_actuals
  - **Verified:** yes (2026-09-23)
- **AC3:** Given dropped, added and carried units and review rounds, then Delivered to plan lists units and points planned against delivered, each drop and add with its recorded reason, and each unit's review round count
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py::OnePageTests::test_delivered_to_plan_shows_changes_and_rounds
  - **Verified:** yes (2026-09-23)
- **AC4:** Given open findings raised in the run and `close_known_issues` in run state, then Known issues handed over lists them by priority with the carried units
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py::OnePageTests::test_known_issues_list_findings_gaps_and_carried_units
  - **Verified:** yes (2026-09-23)
- **AC5:** Given the run, then tokens by model, delegated tokens, DORA, calibration rates and the persona and operator ruling counts appear only in the appendix
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py::OnePageTests::test_cost_dora_and_rulings_live_in_the_appendix
  - **Verified:** yes (2026-09-23)
- **AC6:** Given a figure with no data, then it renders not measured, never 0, in both the markdown and the HTML render, and the HTML carries the same five front-page sections
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py::OnePageTests::test_missing_figures_read_not_measured_in_both_renders
  - **Verified:** yes (2026-09-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
