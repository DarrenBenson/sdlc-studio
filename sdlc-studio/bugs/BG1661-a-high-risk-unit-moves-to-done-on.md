# BG1661: A high-risk unit moves to Done on the first seat's APPROVE, so the second seat's REJECT lands past the round cap and carries the unit instead of repairing it

> **Status:** Fixed
> **Severity:** Low
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py, .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-review.md, changelog.d/BG1661.md
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

- [ ] **AC1** Given a high-risk unit (a `risk.components` map marks its Affects `high`) landed and the qa seat's APPROVE accepted, when `lane accept` records it, then the verdict is recorded as round 1 and the unit is NOT moved to Done (nor returned), and the output says the second seat is owed. Fails on: `lanes.accept` runs `transition.py set` on the first seat's APPROVE, so the unit is Done at once.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py::LaneAcceptSecondSeatBriefTests::test_a_high_risk_first_seat_approve_defers_done
- [ ] **AC2** Given that deferred unit, when the engineering seat's REJECT is recorded, then it is round 1 of a repair (no review-cap report, no carry bug, no split escalation) and the unit is still not Done. Fails on: the REJECT lands as round 2 and `critic.py record` hits the cap and files a carry.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::PerDeliveryRoundTests::test_a_second_seat_reject_on_a_deferred_high_risk_unit_is_round_one
- [ ] **AC3** Given that deferred unit, when the second seat's APPROVE is accepted against the same brief, then the unit moves to Done and its lane returns. Fails on: a fix that defers forever, or moves on the first seat only.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py::LaneAcceptSecondSeatBriefTests::test_the_last_required_seat_approve_moves_a_high_risk_unit
- [ ] **AC4** Given a unit that is not high-risk, when its one seat's APPROVE is accepted, then it moves to Done as today (the control beside AC1). Fails on: a fix that defers every unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_an_approve_records_verifies_transitions_and_returns

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: four executable criteria (defer, second-seat REJECT is round one, last seat moves, non-high control); Affects gains lib/lanes.py, where `accept` runs the transition, and the second-seat and review-cap test modules; 3 pts to 5 as the fix spans accept, the round count and the seat bookkeeping (still within the cap, no split) |
| 2026-11-24 | orchestrator (delegate under D0545) | Affects widened for run twenty-six's SPB lane: the drive's cap check (lib/drive.py:860) counts delivery_rounds rows, so a held second seat would reach the cap early; reference-sprint.md, help/sprint.md and reference-review.md describe the accept and round numbering the fix changes |
