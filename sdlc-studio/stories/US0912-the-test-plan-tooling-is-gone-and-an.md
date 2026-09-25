# US0912: The test-plan tooling is gone and an old Test Plan section is inert

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/lib/surface.py, tools/batch_plan_shape.py, tools/tests/test_batch_plan_shape.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_surface.py, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/help/test-spec.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py, changelog.d/US0912.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer verifying a story
**I want** the criteria and their Verify selectors to be the whole test plan, with `testplan derive`, `probe`, `rule` and `withdraw` gone
**So that** there is one place to state what a story must prove, and no tool left to maintain for a gate that no longer exists

## Acceptance Criteria

- **AC1:** Given `verify_ac.py testplan derive`, `probe`, `rule` or `withdraw`, when invoked, then each exits 2 with a message that it is retired and that the criteria and their Verify selectors are the plan, and `verify_ac.py --help` lists no `testplan`; a fixture story whose body still holds a `## Test Plan` section verifies green through `verify_ac.py run --story <id>`, the section read as plain text. Fails on: deleting the parser so the verbs exit with a usage error, and on a deletion that makes a legacy section break `run`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_the_testplan_verb_is_retired
- **AC2:** Given `mutation.py`, `sprint.py` and `critic.py`, then none references a `verify_ac` testplan helper and `mutation.plan_execution` is gone; and `verify_ac.py revert-check` still exempts a criterion through a reasoned `Revert-check-exempt` field, while a legacy `unnameable` plan row exempts nothing. Fails on: deleting the testplan helpers while `verify_ac.revert_exemptions` still reads plan rows
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_no_caller_reaches_a_testplan_helper
- **AC3:** Given the repository, then `tools/batch_plan_shape.py` and its test are deleted, and `sdlc-studio/reviews/plan-rulings.md` is left byte-identical as frozen history
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_the_shape_tool_is_gone_and_rulings_are_frozen
- **AC4:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `verify_ac.py testplan` or its actions, `test_surface.py` asserts `coverage rule` where it asserted `testplan derive`, and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_the_surface_names_no_retired_verb
- **AC5:** Given the criteria whose stamped Verify selector names a test this story deletes (TestPlanDeriveTests, MultiRowTestPlanTests, UnnameableRowTests, TestPlanProbeTests, PlanRulingTests, TestPlanCellEscapingTests, `test_batch_plan_shape.py`, RowKeyedJoinTests, FromPlanTests and the plan-row exemption tests in RevertCheckTests): BG0596 (6), BG0597 (5), BG0600 (3), BG0606 (3), BG0658 (5), US0629 (3), US0632 (3), US0671 (3, the plan-row exemption tests), US0819 (9) and US0821 (8), then each is retired in the D0259 pattern (`Verify: manual - retired by US0912: <why>`, `Verified: manual (<date>) - retired, superseded by US0912`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py::TestPlanToolingGoneTests::test_no_stamp_names_a_deleted_test

## Notes

- The old AC2 (a legacy section is inert) passed at HEAD, so it is now the control half of AC1. The old AC3 (no test-plan note in the brief) passed at HEAD because the note lives only in `critic._plan_review_brief`; US0915 deletes it, and AC2 here replaces it.
- Hidden callers: `verify_ac.revert_exemptions` (4680-4720) and `mutation.plan_execution` (2762-2855), which is dead after US0911 and deleted here. `sprint.py:2123` and `:4077` are removed by US0911 first.
- `PlanReviewBriefUnauthoredNoteTests` (BG0666) belongs to US0915, so `critic.py` and `test_critic.py` leave this story's Affects.
- Lands after US0910, US0934, US0911 and US0915.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 3 -> 5 points; verbs corrected to `derive`, `probe`, `rule` and `withdraw`; the old AC2 control folded into AC1; the old AC3 replaced by the helper and revert-check criterion; stamps measured and named (about 48 criteria, FromPlanTests and US0632 included); Affects adds mutation.py, test_mutation.py, test_surface.py and the changelog fragment, drops critic.py and test_critic.py |
