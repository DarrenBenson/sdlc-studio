# US0885: A report's time window does not race its own paperwork

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py
> **Epic:** EP0261
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** operator signing a report
**I want** a report that stays VALID when its paperwork is committed in the same second
**So that** signing never depends on how fast the commit followed the close (BG0748)

## Acceptance Criteria

- **AC1:** Given a report generated at second t, when the paperwork is committed within the same second and the run is sealed, then check reads VALID
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py::WindowRaceTests::test_a_same_second_commit_leaves_the_report_valid
  - **Verified:** yes (2026-09-24)
- **AC2:** Given a push-triggered CI run strictly inside the window, then it is still counted in DORA
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py::WindowRaceTests::test_a_run_inside_the_window_still_counts
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
