# US0913: A repair closes without a reviewed repair plan

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/repair_plan.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, tools/test-noise-baseline.json, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py, changelog.d/US0913.md
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer fixing a rejected unit
**I want** a repair to reach Fixed on green criteria and a round-2 APPROVE, with no repair plan written and reviewed first
**So that** a REJECT costs one fix and one re-review, not a plan, a plan review and then the fix

## Acceptance Criteria

- **AC1:** Given a fixture repair bug in a project setting `review.repair_plan_gate: on`, with green criteria, a round-2 independent APPROVE and no repair plan on record, when `transition.py set <id> Fixed` runs, then it succeeds. Fails on: HEAD's repair-plan gate refusing the missing plan
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py::RepairPlanGoneTests::test_a_repair_without_a_plan_reaches_fixed
- **AC2:** Given the scripts tree, then `repair_plan.py` does not exist, no shipped script imports it, and `critic.py` defines no `REPAIR_PLAN_KIND`. Fails on: deleting the module while `critic.py` keeps the kind constant and its brief branch
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py::RepairPlanGoneTests::test_nothing_imports_repair_plan
- **AC3:** Given config-defaults.yaml, then it carries neither `review.repair_plan_gate` nor `review.repair_design_threshold`, and no shipped script reads either key
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py::RepairPlanGoneTests::test_no_repair_plan_keys_are_read
- **AC4:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `repair_plan.py brief`, `record`, `review` or `gate` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py::RepairPlanGoneTests::test_the_surface_names_no_retired_verb
- **AC5:** Given the criteria whose stamped Verify selector names a test this story deletes (`test_repair_plan.py` and RepairProvenanceTests): BG0267 (2), BG0673 (7), BG0678 (6), US0311 (3), US0312 (4), US0313 (3), US0314 (2), US0315 (3), US0343 (4) and US0344 (2), then each is retired in the D0259 pattern (`Verify: manual - retired by US0913: <why>`, `Verified: manual (<date>) - retired, superseded by US0913`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py::RepairPlanGoneTests::test_no_stamp_names_a_deleted_test

## Notes

- `PlanReviewRepairGateTests` (BG0629) moved to US0911 because it tests the test-plan gate, so `test_transition.py` leaves this story's Affects.
- The old AC2 clause "`critic.py record` accepts no `repair-plan` kind" is dropped: US0915 retires `--kind`, and this story lands first.
- Engineering call: US0314's `RepairProvenanceTests` ("a repair records which plan it executed") is deleted here, so its two stamps retire with this story rather than with US0914.
- Leave `transition.is_repair_unit` alone; US0935 deletes it.
- The shared prose edit to `reference-scripts-review.md` moved to US0924.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 3 points held; AC2 drops the `repair-plan` kind clause (US0915 retires `--kind`) and names `REPAIR_PLAN_KIND`; AC5 drops PlanReviewRepairGateTests (moved to US0911) and names the measured stamps (36 criteria, US0314 included); Affects adds test_critic.py, reference-config.md and the changelog fragment, drops test_transition.py and moves reference-scripts-review.md to US0924 |
