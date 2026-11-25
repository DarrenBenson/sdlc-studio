# BG1747: BG1661 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py, .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-review.md, changelog.d/BG1661.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T03:22:44Z

## Summary

BG1661 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the repair's at-cap wording reads the cap through `critic.review_ceiling(root)` (lanes.py:1541), but every test of it runs at the default cap of 2: hard-coding `cap = 2` passes test\_lane\_accept\_second\_seat\_brief.py and test\_lean\_review\_cap.py, and re-tested alone through `sprint.py lane accept` under `review.max_rounds: 3` a held round-2 APPROVE then tells the operator "its REJECT shares round 2, the review cap of 2, so it opens no repair: the unit is carried, or a further round takes a ruling", where HEAD rightly says "its REJECT shares round 2 and opens the repair"; BLOCKING: [new] the new test's docstring says the second seat's REJECT "then carries the unit" (test\_lane\_accept\_second\_seat\_brief.py:225), but its fixture opens no run, so nothing is carried: run with the same steps at 487cf083c, `critic.carried_by` is None, the output carries no carry line and no run is open, and the test asserts no carry, only "REJECT recorded, round 2" and the rounds [1, 2, 2] [LC-018]; RULINGS: Round-one finding "the held APPROVE's output tells the operator the second seat's" is CLOSED. lanes.py now says, at a held round at or past the cap, that the REJECT opens no repair, and below the cap that it opens the repair. The changelog, help/sprint.md:749, reference-sprint.md:119, reference-review.md:503 and the `hold_for_second_seat` docstring now carry the same condition, each TRUE by execution at the default cap. Re-applied mutants all die: the unconditional wording, a strict `>` and a boundary one round early. Round-one finding "two of the diff's cap-counting changes are pinned by no test" is CLOSED. `test_a_ruling_on_a_held_round_at_the_cap_is_not_needed` kills the `past_cap` revert, and `test_a_ruled_round_after_a_shared_round_records_its_own_round` kills the `_append_ruling` round revert, each re-applied and seen red. verify\_ac dry-run gives 4 of 4 pass at 487cf083c. Both new findings are in the repair's own lines and are small: a test that writes `review.max_rounds: 3` into the fixture and asserts the round-2 wording, and a docstring that says what the fixture does (no run, so a further round takes a ruling) or a fixture that opens a run and asserts the carry, close them.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1661 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1661 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the repair's at-cap wording reads the cap through `critic.review_ceiling(root)` (lanes.py:1541), but every test of it runs at the default cap of 2: hard-coding `cap = 2` passes test\_lane\_accept\_second\_seat\_brief.py and test\_lean\_review\_cap.py, and re-tested alone through `sprint.py lane accept` under `review.max_rounds: 3` a held round-2 APPROVE then tells the operator "its REJECT shares round 2, the review cap of 2, so it opens no repair: the unit is carried, or a further round takes a ruling", where HEAD rightly says "its REJECT shares round 2 and opens the repair"
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: BLOCKING: [new] the new test's docstring says the second seat's REJECT "then carries the unit" (test\_lane\_accept\_second\_seat\_brief.py:225), but its fixture opens no run, so nothing is carried: run with the same steps at 487cf083c, `critic.carried_by` is None, the output carries no carry line and no run is open, and the test asserts no carry, only "REJECT recorded, round 2" and the rounds [1, 2, 2] [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG1661 AC1 still passes: Given a high-risk unit (a `risk.components` map marks its Affects `high`) landed and the qa seat's APPROVE accepted, when `lane accept` records it, then the verdict is recorded as round 1 and the unit is NOT moved to Done (nor returned), and the output says the second seat is owed. Fails on: `lanes.accept` runs `transition.py set` on the first seat's APPROVE, so the unit is Done at once.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py::LaneAcceptSecondSeatBriefTests::test_a_high_risk_first_seat_approve_defers_done
  - **Verified:** yes (2026-11-25)
- [ ] **AC4** BG1661 AC2 still passes: Given that deferred unit, when the engineering seat's REJECT is recorded, then it is round 1 of a repair (no review-cap report, no carry bug, no split escalation) and the unit is still not Done. Fails on: the REJECT lands as round 2 and `critic.py record` hits the cap and files a carry.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::PerDeliveryRoundTests::test_a_second_seat_reject_on_a_deferred_high_risk_unit_is_round_one
  - **Verified:** yes (2026-11-25)
- [ ] **AC5** BG1661 AC3 still passes: Given that deferred unit, when the second seat's APPROVE is accepted against the same brief, then the unit moves to Done and its lane returns. Fails on: a fix that defers forever, or moves on the first seat only.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py::LaneAcceptSecondSeatBriefTests::test_the_last_required_seat_approve_moves_a_high_risk_unit
  - **Verified:** yes (2026-11-25)
- [ ] **AC6** BG1661 AC4 still passes: Given a unit that is not high-risk, when its one seat's APPROVE is accepted, then it moves to Done as today (the control beside AC1). Fails on: a fix that defers every unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_an_approve_records_verifies_transitions_and_returns
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
