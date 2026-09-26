# US0950: A fresh project can brief and record its one review with the shipped defaults

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_project_loop.py, changelog.d/US0950.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0265
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer who has just run `init` on a new project
**I want** `critic.py brief` to use the shipped review seat when my project has none of its own, and the whole lean loop to run on the shipped defaults
**So that** my first sprint reaches a signed report without my first having to generate a team or stand a gate down

## Acceptance Criteria

- **AC1:** Given a fresh `init.py run` fixture with no `sdlc-studio/personas/seats/`, when `critic.py brief --unit <id> --seat qa` runs, then it exits 0 and the brief carries the same seat charter `persona_resolve.py resolve --seat qa --render review` prints for that fixture. Fails on: HEAD, which refuses with `no seat card at .../personas/seats/qa.md - available seats: none` (critic.py:3729-3732)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_project_loop.py::FreshLoopTests::test_brief_falls_back_to_the_shipped_seat
- **AC2:** Given the same fixture with a project card `sdlc-studio/personas/seats/qa.md`, when the brief runs, then it carries the project card's charter, not the shipped one. Fails on: a fallback that always reads the shipped card, which would silently ignore a project's own generated team
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_project_loop.py::FreshLoopTests::test_a_project_seat_card_wins
- **AC3:** Given a fresh `init.py run` fixture on the shipped config and one story with a green `Verify:` line, when `sprint.py plan --write`, `verify_ac.py run`, `critic.py brief`, `critic.py record --verdict APPROVE` (reviewer not the author), `transition.py set <id> Review`, `sprint.py close` and `sprint.py sign` run in order, then each exits 0 and the story ends Done. Fails on: HEAD, where `critic.py record` refuses for missing brief provenance and `critic.py brief` refuses for a missing seat card, so the loop dead-ends at its one review
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_project_loop.py::FreshLoopTests::test_the_lean_loop_runs_on_shipped_defaults

## Notes

- Depends on: US0923
- Measured in a throwaway `init run` fixture at 013a46d0: both refusals reproduced; `init run --scaffold` seeds no seat cards either. With `review.require_brief_provenance: false` set by hand the rest of the loop ran to a sealed run (plan, verify, record, Review, close, sign, Done). Ratchet (LC-008): deletes a divergence (critic resolves seats differently from persona_resolve) and adds no check; AC3's measured yield is the two refusals it catches at HEAD. The README's 'Dani, Sam and Lena work out of the box' becomes true for review.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (U7) |
