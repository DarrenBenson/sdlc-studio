# US1154: A high-class unit gets a second independent review seat, and the retro reports what that seat found

> **Status:** Ready
> **Delivers:** CR0696
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py, changelog.d/US1154.md, .claude/skills/sdlc-studio/help/retro.md, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0307
> **Points:** 3
> **Depends on:** US1152
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** a high-class unit gets a second independent review seat, and the retro reports what that seat found
**So that** every release passes the change board on the evidence the run produced, with no separate write-up

## Acceptance Criteria

- **AC1:** Given a high-class unit, when `critic.py brief --unit <id> --seat <second seat>` runs, then the brief is the shipped seat brief (charter, Affects scope, criteria) and names the unit's class and that it is the second independent seat.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py::SecondSeatBriefTests::test_brief_names_class_and_second_seat_role
- **AC2:** Given a high-class unit with two seats' delivery verdicts in the ledger, when `retro.py` composes the run's retro, then it reports, per second seat, the units where it rejected or raised issues after the first seat approved.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py::RetroSecondSeatYieldTests::test_retro_reports_second_seat_catches
- **AC3:** Given a high-class unit with no second-seat verdict, or a run whose second seats caught nothing, when the retro is composed, then it says so in one line each and nothing refuses.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py::RetroSecondSeatNothingTests::test_missing_and_empty_yield_are_stated_not_refused

## Notes

- Serves Abena Osei's End goal 1; delivers part of CR0696 (D0476).
- AC1 must fail on: A hand-assembled prompt; the class line missing; the brief printed for a standard unit with a second-seat line (positive control).
- AC2 must fail on: Counting every second-seat row as a catch; reading the first seat's issues as the second's; the yield absent from the retro.
- AC3 must fail on: A silent retro; a zero printed in place of 'no second-seat verdict'; a refusal or non-zero exit.
- Brief: scripts/critic.py:3755 `brief(repo_root`, unit, seat, tier) and the CLI parser at :5033; the seat card resolves via `_review_seat_card` :3339 and `persona_resolve`. Add the class line from `scripts/lib/risk_class.py` (first story). Do not add a refusing check: the CR adds no gate.
- Ledger: `critic.read_verdicts` :704 (cols unit, verdict, reviewer, author, date, brief, tier, issues at critic.py:115); `seat_verdicts` :869 gives the latest verdict per seat. Second seat = a reviewer role other than the first recorded one on the unit; a catch = second seat REJECT or non-empty issues where the first seat's latest verdict was APPROVE. State this rule in the story.
- Retro hook: scripts/retro.py:1311 `review_cost_split` and :1330 `render_review_cost`, wired at :1612 (bundle) and :1894 (render); add a `second_seat_yield` sibling in the same style `(NOT_IN_FORCE` wording for absence).
- D0460: the second seat is dropped if it catches nothing; the retro reports the yield, the operator decides. No automatic drop.
- Do not let independence break: the second seat must still differ from the unit's author (critic.py independence check).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-14 | Claude Opus 5.5 (run twelve grooming, D0476) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
