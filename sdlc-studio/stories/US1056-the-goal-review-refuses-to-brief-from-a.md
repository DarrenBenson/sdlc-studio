# US1056: The goal review refuses to brief from a traced persona card that fails the standard

> **Status:** Draft
> **Delivers:** CR0631
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/persona_review.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_persona_block.py, changelog.d/US1056.md
> **Epic:** EP0287
> **Points:** 2
> **Depends on:** US1055, US1040
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, approving a Sprint Goal traced to one of her personas
**I want** the goal-review brief to refuse a goal traced to a persona whose card fails the standard, naming the card and its failed rules, and the plan to name that card without listing its End goals
**So that** a persona card the team has judged wrong is not read into the goal review as if it were sound

## Acceptance Criteria

- **AC1:** Given a Sprint Goal naming Maya Okafor, whose card's latest persona review is FAIL, when `sprint.py goal-review brief --goal` runs, then it exits 2 naming Maya's card, the failed rules and the remedy and prints no brief, while a goal naming only Jonah Reyes, whose card passes, is briefed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_persona_block.py::GoalReviewPersonaBlockTests::test_a_goal_traced_to_a_failed_card_is_not_briefed
- **AC2:** Given the same goal, when `sprint.py plan --sprint-goal` runs, then it prints one line naming Maya's card as refused by the persona standard and lists none of its End goals, with the plan's exit code and batch unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_persona_block.py::GoalReviewPersonaBlockTests::test_the_plan_names_the_refused_card_and_still_plans

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the End goal listing reads the card without calling the block, or the refusal fires on an untraced persona's failure
- AC2 must fail on: the plan refuses (advice turned refusal), or lists the refused card's End goals
- Checked at HEAD: `persona_cards` (sprint.py:9975) reads every card under personas/ with no standard check, and `_goal_served_lines` lists traced personas from it.
- Calls the one `persona_review.blocking`. A user persona card has no role rules, so only persona-registry-role and a FAIL review can block it (panel Q11: confirmed).
- Cluster with BG1002, US1036, US1037 and US1040 on `_goal_served_lines`, built last of them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
