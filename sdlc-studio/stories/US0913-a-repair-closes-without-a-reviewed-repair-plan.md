# US0913: A repair closes without a reviewed repair plan

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/repair_plan.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, tools/test-noise-baseline.json, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer fixing a rejected unit
**I want** a repair to reach Fixed on green criteria and a round-2 APPROVE, with no repair plan written and reviewed first
**So that** a REJECT costs one fix and one re-review, not a plan, a plan review and then the fix

## Acceptance Criteria

- **AC1:** Given a fixture repair bug in a project setting `review.repair_plan_gate: on`, with green criteria, a round-2 independent APPROVE and no repair plan on record, when `transition.py set <id> Fixed` runs, then it succeeds
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py::RepairPlanGoneTests::test_a_repair_without_a_plan_reaches_fixed
- **AC2:** Given the scripts tree, then `repair_plan.py` does not exist, no shipped script imports it, and `critic.py record` accepts no `repair-plan` kind
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py::RepairPlanGoneTests::test_nothing_imports_repair_plan
- **AC3:** Given config-defaults.yaml, then it carries neither `review.repair_plan_gate` nor `review.repair_design_threshold`, and no shipped script reads either key
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py::RepairPlanGoneTests::test_no_repair_plan_keys_are_read
- **AC4:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `repair_plan.py brief`, `record`, `review` or `gate` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py::RepairPlanGoneTests::test_the_surface_names_no_retired_verb
- **AC5:** Given every criterion whose stamped Verify selector names a test this story deletes (`test_repair_plan.py` and PlanReviewRepairGateTests; at least those on BG0629, BG0673, BG0678, US0311, US0312, US0313, US0315, US0343, US0344), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py::RepairPlanGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
