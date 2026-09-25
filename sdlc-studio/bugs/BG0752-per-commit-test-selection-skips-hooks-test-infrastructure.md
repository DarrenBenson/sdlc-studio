# BG0752: Per-commit test selection skips hooks, test infrastructure and code reached through another script

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_suite_selection.py
> **Evidence:** US0880 review findings 1-2, RUN-01M3891F
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0880's selection follows direct edges only. A change to `.githooks/*`, `tools/tests/conftest.py`, `pytest.ini`, `tools/skill-tests.sh` or a test helper selects zero modules (before: 68-80), and a `lib/` helper reached only through another script selects none of the tests that exercise it (e.g. `lib/tiers.py` -> `test_planning_tier`). The full suite at push catches them; the commit does not.

Trade-off for planning: the push boundary already runs the full suite, and the skip message discloses the gap ("per-commit selection follows direct edges only, so ... hooks, test infrastructure and code reached on..."). Each widening adds modules to a commit that BG0754 is trying to hold under 90s. The criteria therefore bound the widening: one script hop, and only the modules that name a path.

## Steps to Reproduce

1. Mutate `lib/tiers.py` `promotion_deficit` to `return None`. 2. `gate.py --suite-decision --changed .claude/skills/sdlc-studio/scripts/lib/tiers.py` answers mode none. 3. `test_planning_tier.py` has 3 failures.

Re-run at 65cdf1ca, in a scratch copy: `--suite-decision --changed` answers `skip` for `lib/tiers.py`, `.githooks/pre-commit`, `tools/tests/conftest.py`, `pytest.ini` and `tools/skill-tests.sh`. The test helper `tests/gitutil.py` is not affected: it selects 30 of 230 modules. `lib/tiers.py` is imported by artifact.py, conformance.py, validate.py and transition.py, and test_planning_tier imports conformance.

## Proposed Fix

Route hook and test-infrastructure paths to the modules that name them by path, and follow one level of script-to-script import for `lib/`.

## Acceptance Criteria

- [ ] **AC1** Given a change to `lib/tiers.py` alone, when `gate.py --suite-decision --changed` runs, then it answers `run` and its selectors include `test_planning_tier.py`, reached through conformance.py. In a fixture tree, a module that reaches a changed lib helper only through two script hops is not selected. Fails on: HEAD's direct-edge selection, which answers `skip` (measured); a full transitive closure, which selects the two-hop module and, in this repository, nearly every module.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_suite_selection.py::SuiteSelectionTests::test_a_lib_helper_selects_the_tests_of_the_scripts_that_import_it_one_hop
- [ ] **AC2** Given a change to `.githooks/pre-commit` alone, when `--suite-decision --changed` runs, then it selects the test modules whose source names that path, and no others. A change to `tools/tests/conftest.py` selects the tools/tests modules, a change to `pytest.ini` selects both trees, and a docs-only change still answers `skip`. Fails on: HEAD, which answers `skip` for all three (measured); routing every non-code path to the full suite, which the docs-only control catches.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_suite_selection.py::SuiteSelectionTests::test_a_hook_or_test_infrastructure_change_selects_the_modules_that_depend_on_it

## Impact

US0880's selection follows direct edges only.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (`--suite-decision` answers `skip` for lib/tiers.py, the pre-commit hook, conftest.py, pytest.ini and skill-tests.sh); test helpers are no longer affected; criteria rewritten Given/When/Then with executable Verify lines in a new test_lean module, each bounding the widening against BG0754's commit budget; 3 points stand |
