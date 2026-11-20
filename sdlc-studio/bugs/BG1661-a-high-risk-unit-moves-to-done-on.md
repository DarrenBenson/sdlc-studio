# BG1661: A high-risk unit moves to Done on the first seat's APPROVE, so the second seat's REJECT lands past the round cap and carries the unit instead of repairing it

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T09:04:31Z

## Summary

In run twenty (RUN-01M7VNR0), lane accept recorded US1040's qa APPROVE as round one and moved it to Done while its engineering second seat was still reviewing. The engineering REJECT then recorded as round two, hit the review cap, and critic.py record carried the unit to BG1660 and escalated the split, leaving US1040 Done with a blocking REJECT as its latest verdict. D0541 assumes the second seat's REJECT can be recorded as round one, which this ordering makes impossible.

## Steps to Reproduce

On a high-risk unit, run lane accept with the qa seat's APPROVE (the unit moves to Done), then critic.py record the engineering seat's REJECT: it records round 2, reports the review cap, files a carry bug and escalates.

## Proposed Fix

Hold a high-risk unit's Done until every required seat has judged the same brief: lane accept on the first seat records the verdict but defers the transition, and the last seat's record moves it, so a second-seat REJECT is round one of a repair.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In run twenty (RUN-01M7VNR0), lane accept recorded US1040's qa APPROVE as round one and moved it to Done while its engineering second seat was still reviewing.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: On a high-risk unit, run lane accept with the qa seat's APPROVE (the unit moves to Done), then critic.py record the engineering seat's REJECT: it records round...
- [ ] **AC3** The proposed fix lands, pinned by a test: Hold a high-risk unit's Done until every required seat has judged the same brief: lane accept on the first seat records the verdict but defers the transition...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
