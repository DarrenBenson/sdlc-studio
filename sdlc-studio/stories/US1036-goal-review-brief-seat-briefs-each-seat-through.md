# US1036: goal-review brief --seat briefs each seat through its own review card

> **Status:** Draft
> **Delivers:** CR0627
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_per_seat.py, changelog.d/US1036.md
> **Epic:** EP0284
> **Points:** 3
> **Depends on:** BG1002, BG1015
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer asking four seats to judge a Sprint Goal
**I want** `sprint.py goal-review brief --seat <role>` to brief that seat through its own review card
**So that** each seat reads the goal through its own lens without my agent hand-writing one per seat

## Acceptance Criteria

- **AC1:** Given a project with qa and sre seat cards, when `goal-review brief --seat qa` and `--seat sre` run over the same worklist and goal, then each brief names its own seat and card path and the two texts differ
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_per_seat.py::GoalReviewSeatBriefTests::test_each_seat_is_briefed_through_its_own_card
- **AC2:** Given `--seat security` on a project and skill carrying no security card, when the brief runs, then it exits 2 naming the seats that have cards and prints no brief
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_per_seat.py::GoalReviewSeatBriefTests::test_an_unknown_seat_is_refused_naming_the_roster
- **AC3:** Given no `--seat`, when the brief runs, then it ends by naming the project's review seats and the `--seat <role>` form that frames one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_per_seat.py::GoalReviewSeatBriefTests::test_the_unframed_brief_names_the_per_seat_form

## Notes

- Release: 6.2 (D0355 breakdown G10, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the brief action ignores --seat (HEAD: the text is byte-identical for every seat)
- AC2 must fail on: an unresolvable seat falls back to the unframed brief with exit 0
- AC3 must fail on: the unframed brief carries no pointer to the per-seat form, so an orchestrator hands every seat the same text
- One resolver: lift critic._review_seat_card into a public persona_resolve.review_card(root, seat) that raises naming the roster, and have critic.brief and the goal-review brief both call it (LL0016, LL0042). It stays in persona_resolve as RFC0061 D5's single hook for rendering a seat's learnings into either brief.
- The card is referenced by path with 'adopt the review render', as critic.brief does (panel answer): one rule for both briefs.
- `persona_resolve.py resolve` accepting a project-declared role is BG1015, a dependency and not part of this story; the brief resolves through resolve_card, which already reads declared roles.
- `--seat` is `append` because `record` takes several; on `brief`, more than one value or a record spec carrying `|` is refused naming one role per brief.
- `goal-review record` keeps one `brief` per round, read by nothing at HEAD; it is not split per seat until a reader needs it (LL0056). The changelog says the stored brief is whichever the caller passed.
- Cluster with BG1002 and G11's two goal-review stories on `_compose_seat_brief` and `_goal_served_lines`: BG1002 first, then this story, then G11's (see related).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G10 after the refine panel's review |
