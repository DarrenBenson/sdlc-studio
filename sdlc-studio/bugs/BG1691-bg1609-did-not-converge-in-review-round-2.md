# BG1691: BG1609 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py, changelog.d/BG1609.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_second_seat_differs_from_builder.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_risk_flag.py
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T19:07:17Z

## Summary

BG1609 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The unit leaves "in `review_seats` order" (the `second_review_seat` docstring, sprint.py:3717) pinned by no test, where the base pinned it. At 622cb415 the shipped seats held two candidates, engineering and product, and `test_plan_risk_flag.py` asserting engineering killed the mutant that walks the seats in reverse (KILLED at ef61967b). The unit also takes out the building seat, so every fixture now holds one candidate (product among the shipped seats, security in the new test), and its edit of that assertion to product leaves the order unchecked: the mutant `[*reversed(seats), *persona_resolve.SEATS]` (sprint.py:3725) survives `test_second_seat_differs_from_builder.py`, `test_plan_risk_flag.py`, `test_second_seat.py` and `test_lane_accept_second_seat_brief.py` (20 passed). In isolation, a project whose own seats are engineering, product, qa and security gets product at HEAD and security under the mutant. The repair is a fixture with two own seats outside qa and engineering, asserting the first in `review_seats` order; RULINGS: Round-1 "The new precedence of a project's own seat over the shipped fallback" CLOSED: `test_a_projects_own_seat_comes_before_the_shipped_fallback` pins security over product, and my shipped-first and own-seats-dropped mutants are KILLED. Round-1's [pre-existing] ruling that the order of a project's own seats was unpinned at the base is withdrawn as wrong: it rested on the constant mutant `return "engineering"`, and by execution the order mutant is killed at ef61967b and survives only at HEAD, so the gap is this unit's and is the finding above. AC1 passes through `verify_ac.py run --id BG1609 --dry-run` (1 of 1), and the author's four mutants replay killed. Claim inventory: the changelog and the docstring's building-seat and shipped-fallback sentences TRUE by execution.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1609 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1609 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The unit leaves "in `review_seats` order" (the `second_review_seat` docstring, sprint.py:3717) pinned by no test, where the base pinned it. At 622cb415 the shipped seats held two candidates, engineering and product, and `test_plan_risk_flag.py` asserting engineering killed the mutant that walks the seats in reverse (KILLED at ef61967b). The unit also takes out the building seat, so every fixture now holds one candidate (product among the shipped seats, security in the new test), and its edit of that assertion to product leaves the order unchecked: the mutant `[*reversed(seats), *persona_resolve.SEATS]` (sprint.py:3725) survives `test_second_seat_differs_from_builder.py`, `test_plan_risk_flag.py`, `test_second_seat.py` and `test_lane_accept_second_seat_brief.py` (20 passed). In isolation, a project whose own seats are engineering, product, qa and security gets product at HEAD and security under the mutant. The repair is a fixture with two own seats outside qa and engineering, asserting the first in `review_seats` order
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1609 AC1 still passes: Given a batch holding a unit tagged Risk-class high built with `sprint lane brief` (no --seat) and landed with `lane land --author 'Dani Okafor (engineering)'`, when `critic.py brief --unit <id> --seat <the planned second seat>` runs, then the printed `--reviewer` is not the building seat's holder and the output carries no self-review note. Fails on: the second seat is engineering, the building seat, so the record line names the author as reviewer and notes a self-review.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_second_seat_differs_from_builder.py::SecondSeatNotBuilderTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
