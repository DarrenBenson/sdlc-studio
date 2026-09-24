# US0889: The close forward-ports the skill and keeps one handover per run

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_housekeeping.py
> **Epic:** EP0261
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator finishing a sprint
**I want** the close to forward-port the skill where this repository installs it, and a re-run close to refresh its own handover
**So that** a fix is in force everywhere the moment its run closes, and re-running a close adds no duplicate paperwork

## Acceptance Criteria

- **AC1:** Given a repository shipping tools/forward-port.sh and an installed copy that differs, when sprint close runs, then it applies the forward-port and reports the copy in sync; without the tool it only reports
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_housekeeping.py::CloseHousekeepingTests::test_the_close_forward_ports_where_the_tool_exists
  - **Verified:** yes (2026-09-24)
- **AC2:** Given a run whose close already filed a handover, when the close runs again, then it refreshes that handover in place and writes no new HO file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_housekeeping.py::CloseHousekeepingTests::test_a_rerun_close_refreshes_its_own_handover
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
