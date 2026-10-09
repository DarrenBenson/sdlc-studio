# US1031: sprint plan names the seats that have not read the Sprint Goal

> **Status:** Draft
> **Delivers:** CR0620
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_plan_unread_goal_seats.py, changelog.d/US1031.md
> **Epic:** EP0284
> **Points:** 2
> **Depends on:** US1029
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer approving a plan whose goal two of four seats reviewed
**I want** the plan to name the seats that have not read the goal, QA among them by default, and mark the ones the batch's own files call for
**So that** a QA or SRE seat missing from the goal review is visible before I approve, not found after the run

## Acceptance Criteria

- **AC1:** Given a project declaring engineering, product and sre seats and a goal review recorded by product and engineering only, when `sprint.py plan --sprint-goal` prints the plan, then it names qa and sre as not having read the goal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_unread_goal_seats.py::UnreadGoalSeatTests::test_plan_names_the_seats_that_did_not_read_the_goal
- **AC2:** Given a batch unit `critic.py seats` gives to sre, when the plan prints, then the sre entry says the batch calls for it and names the file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_unread_goal_seats.py::UnreadGoalSeatTests::test_a_seat_the_batch_calls_for_is_marked

## Notes

- Release: 6.2 (D0355 breakdown G10, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the unread seats are read from review_seats (the project's declared seats only), so qa is not named; or `_render_goal_review` never reads them (HEAD, which prints only '2 seat(s) examined')
- AC2 must fail on: the unread seats are listed without consulting seats_for over the batch, so no entry is marked
- Correction to the first draft: `review_seats` (sprint.py:3004) returns only the project's own seats whenever it declares any, so a project declaring engineering, product and sre does not expect qa at HEAD. The unread seats are computed from persona_resolve.seat_roster (the shipped core plus declared roles, persona_resolve.py:100), which is CR0620's 'QA by default'. `needs_reconsult` moves to the same reader, so its JSON and the text agree.
- The renderer is the gap: goal_review_status computes needs_reconsult (sprint.py:3118) and reference-sprint.md calls those seats 'reported', but `_render_goal_review` (sprint.py:3682) never prints them.
- Advice, never a refusal: the plan proceeds. No unread-seat line prints when every expected seat has read the goal; that control sits inside AC1's test, since it passes at HEAD.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G10 after the refine panel's review |
