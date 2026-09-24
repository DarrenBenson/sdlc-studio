# US0912: The test-plan tooling is gone and an old Test Plan section is inert

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/surface.py, tools/batch_plan_shape.py, tools/tests/test_batch_plan_shape.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/help/test-spec.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer verifying a story
**I want** the criteria and their Verify selectors to be the whole test plan, with `testplan derive`, `probe` and `ruling` gone
**So that** there is one place to state what a story must prove, and no tool left to maintain for a gate that no longer exists

## Acceptance Criteria

- **AC1:** Given `verify_ac.py testplan derive`, `testplan probe` or `testplan ruling`, when invoked, then each exits 2 with a message that it is retired and that the criteria and their Verify selectors are the plan, and `verify_ac.py --help` lists no `testplan`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_the_testplan_verb_is_retired
- **AC2:** Given a fixture story whose body still holds a `## Test Plan` section, when `verify_ac.py run --story <id>` runs, then its criteria verify green as they did before and the section is read as plain text
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_a_legacy_test_plan_section_is_inert
- **AC3:** Given `critic.py brief --unit <id> --seat qa` on that story, then the brief renders the criteria and carries no test-plan note
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_the_brief_carries_no_test_plan_note
- **AC4:** Given the repository, then `tools/batch_plan_shape.py` and its test are deleted, and `sdlc-studio/reviews/plan-rulings.md` is left byte-identical as frozen history
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_the_shape_tool_is_gone_and_rulings_are_frozen
- **AC5:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `verify_ac.py testplan` or its actions and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_the_surface_names_no_retired_verb
- **AC6:** Given every criterion whose stamped Verify selector names a test this story deletes (TestPlanDeriveTests, MultiRowTestPlanTests, UnnameableRowTests, TestPlanProbeTests, PlanRulingTests, TestPlanCellEscapingTests, `test_batch_plan_shape.py` and the brief's unauthored-plan note tests; at least those on BG0596, BG0597, BG0606, BG0658, BG0666, US0819, US0821), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
