# BG1614: lane accept records a second seat's verdict against the unit's saved qa brief, not the brief the verdict file names

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, changelog.d/BG1614.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md
> **Evidence:** run eighteen also hit it with critic.py record: US1198's round-two record warned the criteria changed since brief bb6e1cb2124b (now 2c77fe936603) only because verify_ac run had stamped the criteria between the brief and the record; the warning cannot tell a stamp from a changed scope
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T14:54:13Z

## Summary

`sprint.py lane accept --unit <id> --verdict <file> --reviewer '<holder> (engineering)'` records the verdict against the qa brief lane land saved for the unit, ignoring the `BRIEF:` header of the verdict file, which names the engineering brief the second seat actually answered. The row then carries the engineering reviewer with the qa brief's fingerprint, so the ledger says the second seat reviewed a scope it was never given. It also warns that the criteria changed since that qa brief, because the first accept's verify stamped the unit.

## Steps to Reproduce

For a high-risk unit, record the qa seat's APPROVE with `lane accept`, then run `critic.py brief --unit <id> --seat engineering`, have a reviewer write that brief's verdict file, and run `lane accept --unit <id> --verdict <that file> --reviewer 'agent-x (engineering)'`: the output says 'APPROVE recorded, round 2, against brief <the qa brief's fingerprint>'.

## Proposed Fix

Have lane accept read the verdict file's BRIEF header and record against that brief when it names a saved brief for the unit, refusing a header that names none; or refuse a reviewer whose seat differs from the saved brief's seat and point to `critic.py record`.

## Acceptance Criteria

- [ ] **AC1** Given a high-risk unit whose qa verdict is recorded and an engineering brief printed by `critic.py brief --unit <id> --seat engineering`, when `sprint.py lane accept --unit <id> --verdict <that brief's verdict file> --reviewer 'agent-x (engineering)'` runs, then the row is recorded against the brief the file's BRIEF header names, and a header naming no saved brief for the unit is refused. Fails on: the row is recorded against the saved qa brief's fingerprint, ignoring the BRIEF header.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py::LaneAcceptSecondSeatBriefTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (qa seat, groom) | Acceptance criteria authored for planning (run twenty-one) |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Affects widened in-run: the fix makes help/sprint.md and the toolchain runbook's 'accept records against the saved brief' false, so both are corrected inside the unit (D0561) |
