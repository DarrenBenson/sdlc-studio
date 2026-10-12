# US1071: The plan runs the traced End goals once, so the close can say which turned green in the run

> **Status:** Draft
> **Delivers:** CR0629
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_plan_end_goal_baseline.py, changelog.d/US1071.md
> **Epic:** EP0287
> **Points:** 3
> **Depends on:** US1069
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, opening a run against a persona's End goal
**I want** `sprint plan --write` to run the traced executable End goals once and record each result, so the close can say which turned green in the run and which were green already
**So that** a green End goal at the close is evidence the run served the persona, not a check that was passing before the work began

## Acceptance Criteria

- **AC1:** Given a goal naming Maya whose End goal 2 fails and End goal 3 passes when the run opens, when `sprint.py plan --sprint-goal ... --write` runs and later the close runs with both passing, then the plan prints each baseline, the run record holds them, and the close reads End goal 2 as turned green in the run and End goal 3 as green at the plan already.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_end_goal_baseline.py::PlanEndGoalBaselineTests::test_the_close_tells_turned_green_from_already_green
- **AC2:** Given the same goal, when `sprint.py plan --sprint-goal ...` runs without `--write`, then it prints each result and records nothing, and with a red End goal the plan's exit code and batch are the same as with it green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_end_goal_baseline.py::PlanEndGoalBaselineTests::test_a_dry_plan_records_nothing_and_a_red_goal_never_refuses

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: no baseline, so the close cannot tell a goal the run served from one that was met before it
- AC2 must fail on: the baseline recorded by a plan that opens no run, or a red End goal refusing the plan (it is the expected state before the work)
- Serves: Maya Okafor #4.
- CR0629's 'optionally at plan, to show it red before the work'. The first CR0629 piece to shed if the release must shrink.
- Runs only the traced personas' executable End goals, through the same executor as the close, so the plan's cost is a handful of selectors.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
