# BG1511: A test that swaps a module in sys.modules without restoring it reads green alone and in a selection, and red only in the batched release gate

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_test_hygiene.py, changelog.d/BG1511.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_registry_advisory.py, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py, .claude/skills/sdlc-studio/scripts/tests/test_rfc.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:51:57Z

## Summary

BG1506: `CloseReportTests._mod` put a fresh `sprint_report` into sys.modules and left it there, so a later test's patch on its load-time import missed the module sprint.py re-imports at call time. The fault showed only in gate.py --release, which batches every pytest verifier in one session, and in CI's scheduled corpus check; the commit lanes, the push gate's module-parallel run and a lone run all passed. The release gate refused the first 6.4.0 tag candidate on it (US0996::AC3).

## Steps to Reproduce

1. Add a test that assigns sys.modules['`sprint_report`'] to a fresh module and does not restore it.
2. Run that file alone, and the push gate: both green.
3. Run gate.py --release: a later test that patches its load-time import reads red.

## Proposed Fix

A hygiene test that scans the skill's tests for an assignment to sys.modules[...] with no addCleanup, patch.dict or finally that restores it, refusing each one by file and line.

## Acceptance Criteria

- [ ] **AC1** Given a test source that assigns to `sys.modules[...]` with no restoring `addCleanup`, `patch.dict` or `finally`, when the hygiene scanner reads it, then it reports the assignment by file and line. Fails on: an unrestored module swap passing the scan.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_test_hygiene.py::SysModulesRestoreTests::test_an_unrestored_assignment_is_reported_by_file_and_line
- [ ] **AC2** Given three sources that make the same assignment and restore it, one with `addCleanup`, one inside `patch.dict(sys.modules, ...)` and one in a `try` with a restoring `finally`, when the scanner reads them, then it reports none. Fails on: a scanner that refuses every assignment and so gets silenced.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_test_hygiene.py::SysModulesRestoreTests::test_a_restored_assignment_is_not_reported
- [ ] **AC3** Given the skill's own test tree at HEAD, when the hygiene test scans every test module, then it finds no unrestored assignment made inside a class's methods (the test-time swap BG1506 was), each earlier offender having been given its restore and none merely exempted by name; an assignment at module level or in a module-level loader function, which registers a module at import, is reported as an advisory count and does not fail the test. Fails on: the shipped tests still holding a test-time swap that reads red only in the batched release gate.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_test_hygiene.py::SysModulesRestoreTests::test_the_skill_s_tests_restore_every_module_they_swap

## Impact

A test-isolation fault surfaces for the first time at the release gate, on the critical path of a tag.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-four orchestrator) | AC3 scoped to test-time swaps (assignments inside a class's methods, BG1506's shape): the scan found 148 unrestored assignments in 98 modules, almost all import-time `_load` registrations, which the scanner now reports as an advisory count. Affects widens with the test-time offenders' files once the builder counts them |
| 2026-11-23 | Claude Opus 5.5 (run twenty-four orchestrator) | Affects + the 22 test modules holding the 42 unrestored test-time swaps the scanner counts; Points 2 to 5. Builds after the RFC and MD lanes land, since test_validate, test_transition and test_sdlc_md are theirs too |
