# BG0784: A seat card with no role line is silently bypassed for the shipped card, and the unknown-seat refusal names the wrong seats

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG0784.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_file_history.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_history.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_ledger_retired.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T12:08:53Z

## Summary

After US0950, critic.py brief resolves seats through `persona_resolve.resolve_card`: a sdlc-studio/personas/seats/<seat>.md without a role line is ignored and the shipped card briefs the reviewer, with no warning. The unknown-seat refusal names the fixed list (engineering, qa, product), not the project's cards, and `test_unknown_seat_refused_naming_available` passes on that fixed list. Found by US0950's QA review.

## Steps to Reproduce

Write seats/qa.md with no role line; run critic.py brief --seat qa: the shipped charter is briefed silently.

## Proposed Fix

Warn on stderr when seats/<seat>.md exists without a role line; name the project's declared roles and role-less cards in the refusal, and make the test assert them.

## Acceptance Criteria

- [ ] **AC1** Given a project card `sdlc-studio/personas/seats/qa.md` carrying no `<!-- role: -->` line, when `critic.py brief --unit <id> --seat qa` runs, then stderr names that card and says it declares no role so the shipped qa card was used, and the brief is still produced from the shipped charter; and a card that declares `role: qa` produces no such line. Fails on: HEAD's silent fallback (stderr empty, measured on a fresh `init` project, 2026-09-27); warning on every card, which the control case catches
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SeatCardResolutionTests::test_a_role_less_card_is_named_on_stderr
  - **Verified:** yes (2026-09-27)
- [ ] **AC2** Given a project with a card declaring `role: security` and a role-less card, when `critic.py brief --seat wizard` runs, then the refusal lists `security` among the seats it can brief and names the role-less card. Fails on: HEAD's fixed list (`engineering, qa, product`); the existing test's `assertIn('qa', ...)`, which HEAD passes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SeatCardResolutionTests::test_the_unknown_seat_refusal_names_the_project_s_seats
  - **Verified:** yes (2026-09-27)

## Notes

- - 2026-09-27 (QA seat, Sprint 6 planning): reproduced through the CLI on a fresh rc.1 `init` project: a role-less `seats/qa.md` gave exit 0, empty stderr, and a brief naming `templates/personas/amigos/qa.md`; `--seat wizard` refused with `(seats: engineering, qa, product)`. Points 1 -> 2: the refusal must read the project's declared roles, not a constant. If the warning is placed in `persona_resolve.resolve_card` so consult readers share it, `persona_resolve.py` is in Affects; otherwise drop it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | QA seat: groomed for Sprint 6 - two lean criteria with a no-warning control; 1 -> 2 points |
