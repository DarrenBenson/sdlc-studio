# US0951: A clean run's report hands over no false known issues

> **Status:** Done
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issues.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/US0951.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0265
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer reading the one-page report after a sprint
**I want** the known-issues section to list only what is actually open: findings raised in the run, units carried at the cap and red gate lanes
**So that** I know the true state of the work at a glance instead of reading past rows that do not apply

## Acceptance Criteria

- **AC1:** Given a fresh-project fixture run of one story with green criteria, one independent APPROVE and a goal verdict of achieved, when `sprint.py close` files the report, then its `Known issues handed over` section lists 0 close gaps. Fails on: HEAD, where the same run (measured in a throwaway fixture) hands over 13 close gaps, among them `goal-judged: no goal to judge`, `mutation-survivors: no run`, `doc-surface: not applicable` and `review-current: no reviews/LATEST.md`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issues.py::KnownIssuesTests::test_a_clean_run_hands_over_no_close_gap
  - **Verified:** yes (2026-09-25)
- **AC2:** Given the close checklist, then the `mutation-survivors` row and its resolver are deleted, a row that does not apply to the run is omitted, and a row that cannot be measured is shown in the report's appendix as `not measured`, never under known issues. Fails on: relabelling an unmeasured row as ok (hides a real gap); the control is a fixture with a red gate lane, which must still be listed as a known issue
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issues.py::KnownIssuesTests::test_unmeasurable_rows_go_to_the_appendix_and_a_red_lane_stays
  - **Verified:** yes (2026-09-25)
- **AC3:** Given a run whose goal verdict was recorded by `sprint.py close --goal-verdict`, when the checklist is derived, then `goal-judged` reads that verdict. Fails on: HEAD's `no goal to judge` on a run whose verdict is recorded
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issues.py::KnownIssuesTests::test_goal_judged_reads_the_recorded_verdict
  - **Verified:** yes (2026-09-25)

## Notes

- Depends on: BG0771
- Follows the approved one-page design (back-to-basics review: known issues are open findings raised in the run and units carried at the cap). Ratchet (LC-008): a deletion; the mutation-survivors row reads a field nothing writes since US0935 (polish.txt: delete row, resolver, MutationSurvivorCountTests, retire US0660 AC6). Coordinate with BG0771 (tick-verification reads the lean criterion shape): AC1's fixture uses lean criteria, so BG0771 lands first.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (U8) |
