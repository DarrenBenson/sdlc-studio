# BG1753: A high-risk unit goes Fixed on one seat's round-two APPROVE after the second seat's REJECT

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** run twenty-six, BG1287: the engineering seat's round-two APPROVE moved it to Fixed and the qa seat's round-two record was refused at the cap
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T08:32:36Z

## Summary

When a high-risk unit's qa seat approves round one and its engineering second seat rejects it, the repair's round two is recorded first by the rejecting seat, whose APPROVE moves the unit to Fixed alone. The qa seat's round-two verdict on the repaired diff is then refused at the review cap, so the delivered diff carries one seat's judgement, not the two a high-risk unit takes. Seen on BG1287 in run twenty-six.

## Steps to Reproduce

1. A high-risk unit: qa APPROVE at round one (held for the second seat).
2. The engineering second seat REJECTs round one; the builder repairs.
3. The engineering seat's round-two APPROVE is accepted: the unit moves to Fixed.
4. `lane accept` of the qa seat's round-two verdict is refused at the cap.

## Proposed Fix

Hold a high-risk unit's round-two APPROVE until both seats have judged the repaired diff, and give the second seat its round under the cap (per-seat rounds, US1032/US1033, or one shared round both seats record).

## Acceptance Criteria

- [ ] **AC1** Given a high-risk unit whose second seat rejected round one, when the repair's round two is approved by one seat, then the unit is held, not moved to Fixed, until the other seat's round-two verdict on the same diff is recorded, and that verdict is not refused at the cap. Fails on: the unit moving to Fixed on one seat's round-two APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
