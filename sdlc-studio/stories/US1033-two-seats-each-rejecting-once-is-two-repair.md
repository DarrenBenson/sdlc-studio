# US1033: Two seats each rejecting once is two repair rounds, not a non-converging unit

> **Status:** Draft
> **Delivers:** CR0622
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_escalation_per_seat.py, changelog.d/US1033.md
> **Epic:** EP0284
> **Points:** 2
> **Depends on:** US1032
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer reading the escalations a run prints
**I want** the non-convergence and split escalations to count REJECTs per seat
**So that** an escalation names a seat that has rejected twice, not two seats that have each rejected once

## Acceptance Criteria

- **AC1:** Given a unit whose engineering and sre seats each record a round-1 REJECT, when the second is recorded, then no escalation prints, and when the sre seat then records its round-2 REJECT, the output escalates the sre seat as not converging
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_escalation_per_seat.py::EscalationPerSeatTests::test_two_seats_rejecting_once_do_not_escalate
- **AC2:** Given the engineering seat approved and the sre seat rejected in round 1, when the REJECT is recorded, then no 'panel split' escalation prints and the output says the sre REJECT is answered by the sre seat's own round 2
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_escalation_per_seat.py::EscalationPerSeatTests::test_a_second_seats_reject_is_not_a_split

## Notes

- Release: later (D0355 breakdown G10, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: panel_escalation counts REJECTs across every seat (HEAD: PANEL_REJECT_LIMIT 2, critic.py:1392, is met by two seats' first REJECTs)
- AC2 must fail on: seat_verdicts' split check is kept (HEAD prints 'the panel split ... ESCALATED for the operator' beside the carry)
- The panel's answer to the split question: once lanes exist the split notice does not print. Seats are conjunctive, so the sre REJECT holds the unit until the sre seat approves, and there is no tie to break. An escalation fires only when a lane is carried or reaches its own REJECT limit. This retires BG0539's 'a within-round split still escalates' on that reasoning; its across-rounds convergence check stays.
- Touches panel_escalation (critic.py:1424), seat_verdicts (critic.py:685) and escalation_notice, keyed by the lane the per-seat rounds story defines; sprint.panel_escalation is a shim that delegates, and follows any signature change.
- Split out of the lanes story at the panel's request, so each is sized on its own; the two ship in one run, because lanes without this print a false 'not converging' after one round.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G10 after the refine panel's review |
