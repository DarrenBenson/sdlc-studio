# BG0859: The close's status preflight stops every approved bug left In Progress and tells the operator to move it to Review, a status bugs do not have

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0859.md
> **Evidence:** sprint.py close --dry-run on RUN-01M3RPSK, 2026-09-30; `sprint.py _pre_delivery_status`; `critic.is_awaiting_signoff`; CHANGELOG BG0820
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T11:53:27Z

## Summary

RUN-01M3RPSK close --dry-run (2026-09-30): seven bugs, each with an independent delivery APPROVE on the ledger, are each a STOP: 'its code landed ... and its status is still In Progress, which is neither terminal nor awaiting sign-off', remedy '`transition.py set --id BG0842 --status Review`'. The bug vocabulary has no Review (Open, In Progress, Fixed, Verified, Closed, Won't Fix, Superseded), and reference-sprint.md's loop says 'a bug, whose type has no Review, stays In Progress'. BG0820 made the close ask the seal's own bar (an independent APPROVE owes only the signature at any pre-terminal status) - but `sprint._pre_delivery_status`, which feeds this preflight, still asks `critic.is_awaiting_signoff(status)`, a status-only test ('review' in the status). BG0820's repair missed this sibling path.

## Steps to Reproduce

Open a run whose batch is bugs, deliver and APPROVE each, leave them In Progress as the loop says, run `sprint.py close --dry-run`: one status STOP per bug, each naming a transition the bug type refuses.

## Proposed Fix

Have `_pre_delivery_status` ask the same bar BG0820 gave the close (a story or bug with an independent delivery APPROVE awaits only the signature), and name a remedy that exists for the unit's type.

## Acceptance Criteria

- [ ] **AC1** Given an open run whose batch holds a bug at In Progress with an independent delivery APPROVE, when `sprint.py close --dry-run` runs, then no status STOP names that bug. Fails on: HEAD, whose preflight asks the status alone
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UndeliveredBlockerTests::test_an_approved_bug_in_progress_is_not_a_status_stop

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
