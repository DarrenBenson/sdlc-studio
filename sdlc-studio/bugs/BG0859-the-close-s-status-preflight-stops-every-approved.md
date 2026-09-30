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

Re-run at HEAD 46cb9acf on 2026-09-30 in a throwaway git tree built from the lean close fixture: batch US0101 and BG0101, each approved by an independent reviewer, BG0101 left In Progress; the run's base ref recorded and a commit `fix(BG0101): the widget` after it.

1. `sprint.py close --dry-run --retro RETRO0001`: `STOP status: BG0101: its code landed - 1 commit(s) in this run name it - and its status is still 'In Progress', which is neither terminal nor awaiting sign-off`, remedy `transition.py set --id BG0101 --status Review`.
2. `sprint.py close --retro RETRO0001` (the real close, chain unstubbed): exit 0, printing `[status] BG0101: its code landed ... neither terminal nor awaiting sign-off` with the same remedy; the report is filed and `sprint.py sign` later moves BG0101 to Fixed. The preflight never changes the real close's exit code, so only its output shows the defect.

Without a base ref, or with no commit naming the bug, no line is printed at all: `_delivery_evidence` needs both, so a fixture missing either cannot reach the defect.

## Proposed Fix

Have `_pre_delivery_status` ask the same bar BG0820 gave the close (a story or bug with an independent delivery APPROVE awaits only the signature), and name a remedy that exists for the unit's type.

## Acceptance Criteria

- [ ] **AC1** Given an open run with a recorded base ref whose batch holds a bug at In Progress with an independent delivery APPROVE and a commit in the run naming it, when `sprint.py close` runs for real and `sprint.py close --dry-run` runs, then neither output carries a `[status]` or `STOP status` line naming that bug; and a bug in the same batch at In Progress with no APPROVE is still named by both. Fails on: HEAD, whose preflight asks the status alone and prints both lines; on an assertion on the real close's exit code, which is 0 with the fix reverted; and on a fix that drops the status check, which stops naming the unapproved bug
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UndeliveredBlockerTests::test_an_approved_bug_in_progress_is_not_a_status_stop

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Goal review round 2, finalised by hand: premise re-run at HEAD on the real close as well as the dry run (the real close exits 0 and prints `[status] BG0101 ...`); AC1 asserts the OUTPUT of both, not the exit code, keeps an unapproved bug as the negative control, and requires a base ref and a commit naming the bug so the fixture reaches the check. |
