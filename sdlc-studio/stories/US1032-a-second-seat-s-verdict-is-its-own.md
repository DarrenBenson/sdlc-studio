# US1032: A second seat's verdict is its own round, so its REJECT is repaired rather than carried

> **Status:** Draft
> **Delivers:** CR0622
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_rounds_per_seat.py, changelog.d/US1032.md
> **Epic:** EP0284
> **Points:** 5
> **Depends on:** US1030, BG1003, US1012, US1016
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer who wants a second lens on a risky unit
**I want** the verdict ledger to number rounds and apply the round cap per seat, the seat read from the `(role)` its reviewer records
**So that** an SRE seat that rejects a unit the engineering seat approved gets a repair round, instead of its first verdict carrying the unit to a bug

## Acceptance Criteria

- **AC1:** Given a unit in an open run that `Dani Okafor (engineering)` approved in round 1, when `Idris Locke (sre)` records a REJECT, then it is recorded and shown by `critic.py show` as round 1 (sre), and the unit stays in the batch with no bug filed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rounds_per_seat.py::RoundsPerSeatTests::test_a_second_seats_reject_is_its_own_round_one
- **AC2:** Given the sre seat's round-1 REJECT stands, when the engineering seat records its round-1 APPROVE, then the row is written and `critic.py show --unit` still reports the unit rejected
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rounds_per_seat.py::RoundsPerSeatTests::test_a_second_seat_records_while_the_first_seats_reject_stands
- **AC3:** Given the sre seat rejected in round 1 after an engineering APPROVE, when the sre seat records a round-2 REJECT, then the unit is carried at the cap with the sre findings filed as a bug
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rounds_per_seat.py::RoundsPerSeatTests::test_a_seats_second_reject_still_carries_the_unit
- **AC4:** Given a project with product and qa cards and a round-1 REJECT by `Mara Feld (qa) re-checking the product finding`, when `Rowan Ash (product)` records, then it is written as the product seat's round 1, because the first row's seat is the qa its reviewer names
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rounds_per_seat.py::RoundsPerSeatTests::test_a_reviewer_naming_its_seat_stays_in_it
- **AC5:** Given a REJECT by `Dani Okafor (engineering)`, when `Kit Devane (engineering)` records, then it is refused naming Dani, while `Idris Locke (sre)` recording next is written as the sre seat's round 1, with or without an sre card on disk
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rounds_per_seat.py::RoundsPerSeatTests::test_the_exception_is_by_recorded_seat_not_by_reviewer

## Notes

- Release: later (D0355 breakdown G10, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: delivery_rounds numbers every row of the unit as one sequence (HEAD), so the REJECT is round 2 at the cap and carries the unit
- AC2 must fail on: round_refusal's same-reviewer rule reads the unit's last row rather than the recording seat's own (HEAD: the APPROVE is refused), or the engineering APPROVE is allowed to answer the sre REJECT
- AC3 must fail on: the cap is not applied to a second seat's rows, so its round-2 REJECT is written without carrying
- AC4 must fail on: the seat is read through critic.seat_for, a first-match heuristic that resolves the first reviewer to product, so Rowan's verdict is refused as round 2 of Mara's REJECT
- AC5 must fail on: seats are keyed on the reviewer string (so Kit starts a fresh round), or a row's seat is checked against the cards at read time (so with no sre card Idris joins the shared lane and is refused)
- A row's lane is the first `(<role>)` or `(<role> seat)` group in its Reviewer cell, the form the brief footer writes (G10 brief story AC3). A row with no such group joins one shared lane, so a project whose reviewers name no seat, and test_lean_review_cap's `rev-a`/`rev-b`, keep US0872's behaviour exactly.
- Where this departs from the panel: no fallback to critic.seat_for. The panel asked for the `(role)` group first and seat_for otherwise; seat_for is the first-match heuristic that misattributes a reviewer (the panel's own probe), and a fallback would put it back under the cap for every legacy-shaped string. The Reviewer cell is committed at record time, so the lane is stamped when the row is written, reads the same in every clone, and does not move when a card is added or removed mid-delivery (AC5). The cost: a second seat counts as one only when its reviewer names its role, which the footer does. `record` warns, without refusing, when the named role is in no card's roster.
- No new ledger cell: G6 story 2's ninth `Source` cell is the only widening, and BG1003's authorising decision goes in that cell (G6-review), so the ledger shape changes once.
- Touches delivery_rounds, `_number_rounds` (so `critic.py show` and the carried bug's text print the lane round, e.g. `round 1 (sre)`), round_refusal (the cap and the same-reviewer rule per lane, and the carried-unit discharge past the cap per lane), `_carry_if_capped`, carried_to and the record line. Seats stay conjunctive with no new rule: `_unanswered_rejects` (critic.py:764) pairs a REJECT only with its own reviewer's later APPROVE.
- G6 story 4's ledger rejoinder then picks the standing REJECT of the briefed seat's lane; this story makes that change.
- The report's `unit_rounds` figure (`_frozen_rounds`, sprint_report.py:3364) keeps counting rows, so a sealed page re-derives unchanged; the changelog says a unit two seats each reviewed once reads 2 there.
- HEAD evidence (draft fixture, re-probed by the panel at d327d5d0): an engineering APPROVE then an sre REJECT recorded round 2, carried the unit and filed BG0001; the reverse order was refused.
- Riskiest story in the group: every delivery review passes through the cap it changes. Paired with the escalation story in one run, after BG1003 and G6 story 2.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G10 after the refine panel's review |
