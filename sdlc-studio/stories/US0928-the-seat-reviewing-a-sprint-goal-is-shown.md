# US0928: The seat reviewing a Sprint Goal is shown the PRD outcomes and the personas' End goals

> **Status:** In Progress
> **Depends on:** US0927 - reuses the goal-trace function (CR0594 refinement)
> **Delivers:** CR0594
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_seat_prd.py, changelog.d/US0928.md
> **Epic:** EP0264
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As** Maya Okafor, relying on the seats to judge the Sprint Goal before I approve the plan
**I want** the goal seat's brief to carry the PRD outcomes and the End goals of the personas the product serves
**So that** the seat can judge whether the goal serves a user, not only whether it is achievable, and I am asked only when the answer is genuinely mine - End goal 3, "Drive a whole batch of work to "done" autonomously, pausing only when a decision is genuinely hers"

## Acceptance Criteria

- **AC1:** Given S1's fixture, when `sprint.py goal-review brief --goal "<goal>" --brief-worklist <file>` runs, then the brief lists every PRD outcome with its id and text, and the End goals of each Primary and Secondary persona card numbered as on the card, and names any Negative persona as declined; a brief carrying outcome ids without their text, or leaving out the persona End goals, fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_seat_prd.py::GoalSeatPrdTests::test_the_brief_carries_outcomes_and_end_goals
- **AC2:** Given a goal that `sprint plan` traces to O2, then the brief states that trace, computed by the same function the plan calls (replacing that function in the test changes the brief), and given a goal that traces to none, the brief says so and asks the seat to name the outcome it serves in its `done_means` or note; a second matcher inside the brief fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_seat_prd.py::GoalSeatPrdTests::test_the_brief_states_the_plans_own_trace
- **AC3:** Given a project with no PRD outcomes and no persona cards, then the brief states in one line that there is nothing to trace against and still renders the batch, the grooming state and the lessons exactly as before
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_seat_prd.py::GoalSeatPrdTests::test_no_prd_says_so_and_keeps_the_brief
- **AC4:** Given a seat verdict carrying only the existing three answers (`achievable`, `done_means`, `one_increment`) and no outcome named, when `sprint.py goal-review record` runs, then it records exactly as before - reading the PRD adds no required field and no refusal; an implementation that demands a `serves` answer fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_seat_prd.py::GoalSeatPrdTests::test_record_adds_no_required_field

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Product seat | Groomed from CR0594's refinement: user story and criteria authored |
