# US1120: The lane brief leaves the commit to lane land and holds the builder to a call budget with a hand-off note in place of a growing context

> **Status:** Ready
> **Delivers:** CR0661
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, changelog.d/US1120.md
> **Epic:** EP0298
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The lane brief leaves the commit to lane land and holds the builder to a call budget with a hand-off note in place of a growing context
**So that** no builder waits on a hook or carries its context past a budget

## Acceptance Criteria

- **AC1:** Given `sprint.py lane brief --units <id>`, then its closing commands tell the builder to stage exactly its Affects, write the commit message and each unit's claims and mutants files to the hand-in path, and stop without committing, naming `sprint lane land` as what commits; the brief prints no `git commit` and no `self-check record` command for the builder
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py::LaneBriefBudgetTests::test_the_brief_hands_the_commit_to_lane_land
- **AC2:** Given lanes of 1 and 5 points, then each brief states a tool-call budget formed from one per-point constant, and the hand-off rule: at the budget, write a hand-off note of what is done, the criteria left and the next step to the hand-in path, and return
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py::LaneBriefBudgetTests::test_the_budget_scales_with_points_and_names_the_hand_off
- **AC3:** Given `reference-agent-prompt-template.md`, then it says a repair or second build resumes its builder only below a stated context size, and otherwise starts a fresh builder from the hand-off note
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py::LaneBriefBudgetTests::test_the_prompt_template_names_the_fresh_builder_rule

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | sdlc-studio | Created via `new` (deterministic) |
