# US0911: A unit reaches Done without a test plan or a falsifiability probe

> **Status:** Done
> **Depends on:** US0934 - shares _pre_write_gates; the depth gate shapes its fixtures (EP0263 readiness)
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py, tools/tests/test_check_spec_claims.py, .claude/skills/sdlc-studio/help/epic.md, .claude/skills/sdlc-studio/templates/core/epic.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py, changelog.d/US0911.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, sdlc-studio/bugs/BG0568-an-epic-can-never-reach-done-the-test.md, sdlc-studio/bugs/BG0596-testplan-run-from-plan-keys-by-criterion-so.md, sdlc-studio/bugs/BG0629-a-plan-review-reject-can-never-be-retired.md, sdlc-studio/bugs/BG0630-the-test-plan-gate-is-skipped-on-in.md, sdlc-studio/bugs/BG0665-seven-of-thirteen-review-settings-are-absent-from.md, sdlc-studio/stories/US0630-a-unit-reaching-delivery-without-a-reviewed-test.md, sdlc-studio/stories/US0633-a-criterion-whose-mutant-cannot-be-named-is.md, sdlc-studio/stories/US0820-sprint-plan-refuses-a-batch-carrying-an-unruled.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer planning and closing a sprint
**I want** units to plan and close on their acceptance criteria and Verify selectors, with no test-plan review, planned-mutant join or plan-time falsifiability probe
**So that** criteria quality is judged once, in the one review, instead of by a second pre-code gate and a probe that refuse before any code exists

## Acceptance Criteria

- **AC1:** Given a fixture story and a fixture bug with no `## Test Plan`, created after the `review.test_plan_after` date the fixture sets, with green criteria and an independent delivery APPROVE, the bug carrying `> **Verification depth:** functional` and the config setting `review.mutation_evidence: off` (so only this gate can refuse, whether or not US0934 or US0935 has landed), when each is moved to Done or Fixed through the CLI, then neither is refused and no output names a test plan or a planned mutant. Fails on: removing the Done-side gate and leaving the Fixed-side planned-mutant gate
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_a_unit_without_a_test_plan_closes
  - **Verified:** yes (2026-09-25)
- **AC2:** Given a batch unit whose `## Test Plan` holds one bare `unnameable` row and one `unnameable: <reason>` row, and a fixture config setting `review.plan_falsifiability: block`, when `sprint.py plan` runs, then it is refused for neither row and no falsifiability probe runs; the same batch with a unit lacking Points is still refused naming Points, so the grooming gate survives. Fails on: deleting only the malformed-row branch (HEAD refuses both rows), and on a deletion that takes the Points refusal with it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_plan_neither_probes_nor_refuses_unnameable_rows
  - **Verified:** yes (2026-09-25)
- **AC3:** Given `mutation.py run --from-plan`, when invoked, then it exits 2 with a message that the flag is retired naming `mutation.py run`, and `mutation.py run --help` no longer offers `--from-plan`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_from_plan_is_retired
  - **Verified:** yes (2026-09-25)
- **AC4:** Given config-defaults.yaml, then it carries neither `review.test_plan_after` nor `review.plan_falsifiability`, and no shipped script reads either key (`_plan_gate_active`, `_planned_mutant_gate` and `_test_plan_gate` are gone). Fails on: deleting the keys from the defaults while `transition.py` still reads them with a fallback
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_no_test_plan_keys_are_read
  - **Verified:** yes (2026-09-25)
- **AC5:** Given the criteria whose stamped Verify selector names a test this story deletes (TestPlanGateTests, TestPlanGateEntryTests, PlannedMutantGateNamesTheRowTests, PlanReviewRepairGateTests, UnnameableMutantTests and PlanFalsifiabilityGateTests): BG0596 (1), BG0629 (5), BG0630 (6), US0630 (4), US0633 (2) and US0820 (6), then each is retired in the D0259 pattern (`Verify: manual - retired by US0911: <why>`, `Verified: manual (<date>) - retired, superseded by US0911`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_test_plan_gate.py::TestPlanGateGoneTests::test_no_stamp_names_a_deleted_test
  - **Verified:** yes (2026-09-25)

## Notes

- The old AC3 (an unsized unit is still refused) passed at HEAD, so it is now the control half of AC2.
- `DoctrineTests::test_the_named_gate_actually_exists` in `tools/tests/test_check_spec_claims.py` names `_plan_gate_active`; repoint or retire it here. BG0665's test in `test_config.py` reads `test_plan_after`.
- Leave `transition.is_repair_unit` alone. US0913 and US0935 still read it, and US0935 deletes it.
- Engineering call: `FromPlanTests` (US0632) tests `mutation.plan_execution` directly, not `--from-plan`, so its stamps retire with US0912, which deletes `plan_execution`. The readiness review had listed US0632 here and under US0912; it goes to US0912 only.
- The shared prose edits to `help/sprint.md` and `reference-sprint-toolchain.md` moved to US0924.
- `CR0556`, `EP0242` and `US0800` wait for this story and US0936 (product seat ruling).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 5 points held; AC1 fixture isolates this gate (depth line, `mutation_evidence: off`); AC2 holds a bare and a reasoned `unnameable` row; the old AC3 control folded into AC2 because it passed at HEAD; stamps measured and named (24 criteria, PlanReviewRepairGateTests moved here from US0913); Affects adds test_check_spec_claims.py, test_config.py, reference-config.md and the changelog fragment, and moves help/sprint.md and reference-sprint-toolchain.md to US0924 |
