# US0911: A unit reaches Done without a test plan or a falsifiability probe

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/epic.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/templates/core/epic.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer planning and closing a sprint
**I want** units to plan and close on their acceptance criteria and Verify selectors, with no test-plan review, planned-mutant join or plan-time falsifiability probe
**So that** criteria quality is judged once, in the one review, instead of by a second pre-code gate and a probe that refuse before any code exists

## Acceptance Criteria

- **AC1:** Given a fixture story and a fixture bug with no `## Test Plan`, created after the `review.test_plan_after` date the fixture sets, with green criteria and an independent delivery APPROVE, when each is moved to Done or Fixed through the CLI, then neither is refused and no output names a test plan or a planned mutant
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_a_unit_without_a_test_plan_closes
- **AC2:** Given a batch unit whose `## Test Plan` marks a row `unnameable` with no reason, and a fixture config setting `review.plan_falsifiability: block`, when `sprint.py plan` runs, then it is not refused for that row and no falsifiability probe runs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_plan_neither_probes_nor_refuses_unnameable_rows
- **AC3:** Given a batch unit with no Points, when `sprint.py plan` runs, then it is still refused naming Points, so the grooming gate survives the deletion
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_plan_still_refuses_an_unsized_unit
- **AC4:** Given `mutation.py run --from-plan`, when invoked, then it exits 2 with a message that the flag is retired naming `mutation.py run`, and `mutation.py run --help` no longer offers `--from-plan`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_from_plan_is_retired
- **AC5:** Given config-defaults.yaml, then it carries neither `review.test_plan_after` nor `review.plan_falsifiability`, and no shipped script reads either key
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_no_test_plan_keys_are_read
- **AC6:** Given every criterion whose stamped Verify selector names a test this story deletes (TestPlanGateTests, PlannedMutantGateNamesTheRowTests, FromPlanTests, UnnameableMutantTests and PlanFalsifiabilityGateTests; at least those on BG0596, BG0630, US0820), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
