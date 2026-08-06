# US0630: a unit reaching delivery without a reviewed test plan is REFUSED by the command that starts the work

> **Status:** Ready
> **Delivers:** CR0525
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0207
> **Depends on:** US0629, US0631
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** maintainer starting work on a unit
**I want** the command that starts the work to refuse until a reviewed test plan exists
**So that** the demand lands where it can still be met, rather than at the close where it becomes a finding somebody has to argue about

## Acceptance Criteria

### AC1: starting the work is refused while no test plan exists

- **Given** a unit with no `## Test Plan` section
- **When** `transition.py set --id <id> --status "In Progress"` runs
- **Then** it exits non-zero, names the missing plan and prints the command that produces it, in the same refusal shape the existing verification-depth demand already uses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TestPlanGateTests::test_starting_work_without_a_plan_is_refused
- **Caller:** `transition.py set` (the CLI verb the sprint loop and the operator both use to start a unit)
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - removing the gate call must turn this test red
- **Verified:** yes (2026-08-06)

### AC2: an unreviewed plan is refused on the same terms as a missing one

- **Given** a unit whose test plan exists but carries no APPROVE row in `plan-review-verdicts.md` from a reviewer differing from the plan's author
- **When** the same transition runs
- **Then** it refuses, distinguishing "no plan" from "plan not reviewed" in the message, because the two have different fixes and one message for both sends the reader to the wrong command
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TestPlanGateTests::test_an_unreviewed_plan_is_refused_distinctly
- **Caller:** `transition.py set`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - collapsing the two refusal messages into one must turn this test red
- **Verified:** yes (2026-08-06)

### AC3: the demand is stated before the work, not discovered by hitting it

- **Given** a unit that has not been started
- **When** `transition.py requirements --id <id>` runs
- **Then** it names the test-plan requirement among the gates that unit will face, derived by running the real gate rather than restating it, so an operator can see the cost before spending any
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TestPlanGateTests::test_requirements_states_the_test_plan_demand
- **Caller:** `transition.py requirements`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - dropping the requirement from the derived list must turn this test red
- **Verified:** yes (2026-08-06)

### AC4: the gate is opt-in per project and dated, so an existing backlog is not retro-refused

- **Given** a project whose config sets no test-plan cutoff, and one that sets `review.test_plan_after`
- **When** the transition gate evaluates a unit created before that cutoff
- **Then** it passes untouched, and only units created on or after the cutoff are held, because a gate that refuses every unit in an existing backlog is one that gets switched off wholesale
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TestPlanGateTests::test_a_unit_before_the_cutoff_is_not_held
- **Caller:** `transition.py set`, reading `review.test_plan_after` from project config
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - ignoring the cutoff must turn this test red
- **Verified:** yes (2026-08-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | sdlc-studio | Groomed: criteria authored against the `transition.py` gate slice |
| 2026-08-06 | sdlc-studio | Declared `Depends on:` at plan time - the planner reported all six units parallel because no dependency was stated, which is false: the plan is derived (US0629) before it can be reviewed, gated, executed or measured |
