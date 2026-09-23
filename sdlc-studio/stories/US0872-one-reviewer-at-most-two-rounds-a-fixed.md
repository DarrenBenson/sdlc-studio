# US0872: One reviewer, at most two rounds: a fixed unit clears and a non-converging unit is carried

> **Status:** Draft
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py
> **Epic:** EP0260
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

- **AC1:** Given a unit with no verdict, when critic record writes one, then the row carries round 1; after a REJECT the next row carries round 2; every round is kept as its own row, and `critic.review_rounds(root`, unit) returns the count
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::ReviewRoundTests::test_each_verdict_carries_its_round_and_is_kept
- **AC2:** Given a round-1 REJECT, when the same reviewer records APPROVE at round 2 with no repair record, then the unit's verdict reads APPROVE and transition to Done is not refused for an unanswered REJECT
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::ReviewRoundTests::test_a_round_two_approve_clears_the_reject
- **AC3:** Given a round-1 REJECT by reviewer A, when reviewer B records round 2, then it is refused naming A, because round 2 re-checks the fixes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::ReviewRoundTests::test_round_two_from_another_reviewer_is_refused
- **AC4:** Given a round-2 REJECT, when it is recorded, then a bug is filed carrying the findings, the unit is dropped from the open run's batch with the reason carried at the review cap naming the bug, and the command exits 0 so the run continues
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::ReviewRoundTests::test_a_round_two_reject_carries_the_unit_as_a_known_issue
- **AC5:** Given two rounds recorded for a unit, when a third verdict is written, then it is refused with exit 2 naming the cap, which is `review.max_rounds` defaulting to 2
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::ReviewRoundTests::test_a_third_round_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
