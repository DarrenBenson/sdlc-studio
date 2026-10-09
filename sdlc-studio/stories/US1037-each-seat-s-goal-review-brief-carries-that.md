# US1037: Each seat's goal-review brief carries that seat's own questions

> **Status:** Draft
> **Delivers:** CR0627
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/templates/personas/amigos/engineering.md, .claude/skills/sdlc-studio/templates/personas/amigos/product.md, .claude/skills/sdlc-studio/templates/personas/amigos/qa.md, .claude/skills/sdlc-studio/templates/personas/amigo-template.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_seat_questions.py, changelog.d/US1037.md
> **Epic:** EP0284
> **Points:** 3
> **Depends on:** US1036, US1040
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose seats each own a different question about the goal
**I want** each seat's goal-review brief to carry that seat's questions, read from its card
**So that** QA asks which criteria cannot be executed and an SRE seat how each alarm is proven, without the orchestrator inventing the lens

## Acceptance Criteria

- **AC1:** Given a project with no seat cards, when `goal-review brief --seat qa` runs, then it carries the shipped QA card's goal-review questions and none of the product card's
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_seat_questions.py::SeatQuestionTests::test_the_qa_brief_carries_the_qa_questions_only
- **AC2:** Given a project sre card with a `## Goal Review Questions` section, when `goal-review brief --seat sre` runs, then the brief quotes those questions
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_seat_questions.py::SeatQuestionTests::test_a_project_card_supplies_its_own_questions
- **AC3:** Given a project qa card without that section, when `goal-review brief --seat qa` runs, then the shipped QA card's questions are used and the brief says they are the shipped seat's
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_seat_questions.py::SeatQuestionTests::test_a_card_without_questions_inherits_the_shipped_role
- **AC4:** Given a project sre card without the section and no shipped sre card, when `goal-review brief --seat sre` runs, then the brief says no goal-review questions are declared for sre and to judge by the card's Lens
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_seat_questions.py::SeatQuestionTests::test_a_role_with_no_questions_says_so

## Notes

- Release: 6.2 (D0355 breakdown G10, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: one question list is shared by every seat
- AC2 must fail on: questions are read from the shipped cards only
- AC3 must fail on: a project card without the section yields no questions, so this repository's own cards would brief none
- AC4 must fail on: the brief prints nothing in place of the questions, so absent and empty read alike
- On the card, as the panel answered: the questions are seat identity, and a reviewed card is where RFC0061's persona review holds them to a standard. That review's standard should list the section as optional identity, and a learning that refines a question is a card change.
- Shipped questions, from CR0627: engineering - build order, rollback for a unit that changes production runtime, shared files; product - which persona End goal the increment serves; qa - which criteria are manual-only and could be executable, and which would pass with no fix. An SRE seat's (which failures alarm, and how each alarm is proven by inducing the failure) belong in a consuming project's own SRE card.
- The section is optional: validate seats and the review-render check stay on Lens, Pushes Back When and Shadow, so no existing card becomes invalid. This repository's own cards inherit the shipped questions and need no edit.
- Accepted and stated in the amigo template: critic.brief points a delivery reviewer at the whole card file (and frame() returns the whole card), so a delivery reviewer also sees the section; its heading says it is for the goal review.
- In the goal-review cluster after this group's per-seat brief story and G11's testable End goals story, which adds data to the brief's shared part; the QA criteria story follows this one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G10 after the refine panel's review |
