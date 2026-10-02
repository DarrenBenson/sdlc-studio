# US0982: The lane brief tells a repair to carry only its blocking fix and pins

> **Status:** Ready
> **Delivers:** CR0608
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_brief_repair_scope.py, changelog.d/CR0608.md
> **Epic:** EP0272
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the lane brief to say in one line that a repair carries only its blocking fix and the pins that kill it
**So that** a repair stops breaking what the first build got right (LC-005, three hits) without a new gate (D0310)

## Acceptance Criteria

### AC1: The lane brief names the repair scope

- **Given** an open run whose batch holds a unit
- **When** `sprint.py lane brief --units <it>` runs
- **Then** its "Obligations on this lane" list carries one line saying a repair answering a REJECT carries only the blocking findings and the pins that kill them, and files the rest (D0303); the brief adds no flag, refusal or gate. Fails on: the current brief, which names no repair scope
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_brief_repair_scope.py::LaneBriefRepairScopeTests::test_the_brief_names_the_repair_scope

> CR0608's other two criteria are answered by D0310, not by code: no check is proposed, so none retires anything (AC2), and LC-005 graduates through the close's existing lesson lifecycle when CR0608 closes Complete (AC3).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-02 | engineering seat (orchestrator) | Groomed from CR0608 under D0310: one brief line, no gate |
