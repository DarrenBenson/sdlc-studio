# BG1614: lane accept records a second seat's verdict against the unit's saved qa brief, not the brief the verdict file names

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, changelog.d/BG1614.md
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

- [ ] **AC1** The behaviour described is corrected: `sprint.py lane accept --unit <id> --verdict <file> --reviewer '<holder> (engineering)'` records the verdict against the qa brief lane land saved for the unit...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: For a high-risk unit, record the qa seat's APPROVE with `lane accept`, then run `critic.py brief --unit <id> --seat engineering`, have a reviewer write that...
- [ ] **AC3** The proposed fix lands, pinned by a test: Have lane accept read the verdict file's BRIEF header and record against that brief when it names a saved brief for the unit, refusing a header that names...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
