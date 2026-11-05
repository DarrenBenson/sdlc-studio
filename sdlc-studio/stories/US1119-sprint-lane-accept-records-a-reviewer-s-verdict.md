# US1119: sprint lane accept records a reviewer's verdict and, on APPROVE, runs the criteria, moves the unit to its terminal status and returns its lane

> **Status:** Done
> **Delivers:** CR0661
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, changelog.d/US1119.md
> **Epic:** EP0298
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** sprint lane accept records a reviewer's verdict and, on APPROVE, runs the criteria, moves the unit to its terminal status and returns its lane
**So that** finishing a reviewed unit is one orchestrator command rather than four

## Acceptance Criteria

- **AC1:** Given a unit whose QA brief lane land wrote and a verdict file reading `VERDICT: APPROVE`, when `sprint.py lane accept --unit <id> --verdict <file> --reviewer <name>` runs, then it records the verdict against that brief's fingerprint and tier, runs the unit's criteria, moves a story to Done or a bug to Fixed, and returns its lane, passing `--agent` through to the return
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_an_approve_records_verifies_transitions_and_returns
  - **Verified:** yes (2026-11-05)
- **AC2:** Given `VERDICT: REJECT`, then it records the verdict, moves nothing, and prints only the blocking findings and the round; at the review cap it prints the id of the bug that carries the unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_a_reject_records_and_prints_only_the_blocking_findings
  - **Verified:** yes (2026-11-05)
- **AC3:** Given an APPROVE and a red criterion, then the unit is not moved, the exit is non-zero, and the red criterion is named
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_a_red_criterion_stops_the_transition
  - **Verified:** yes (2026-11-05)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | sdlc-studio | Created via `new` (deterministic) |
