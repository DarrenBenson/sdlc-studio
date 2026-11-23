# BG1729: US1326 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/US1326.md
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T15:02:37Z

## Summary

US1326 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] a comment holding a comma inside a parenthesised import list is unpinned (sprint.py:1134, sprint.py:1176): narrowing `_REACH_COMMENT` from `#[^\n]*` to `#[^\n,]*`, so a comment is cut at its first comma, survives all 18 PlanTestModuleAdvisoryTests (18 passed). Run through `sprint.py plan --stories Ready --no-fetch --skip-personas` in a fixture, that mutant drops a module holding `from lib import (  # noqa: E402, F401` and `surface,` for a declared `scripts/lib/surface.py`, which brings round one's defect back for the commonest comment an import list carries, and it lists a module whose only `surface` stands in the comment `# see a, surface`. HEAD lists the first and not the second, so the code is right and only the pin is missing: the new test (test\_sprint.py:2590) holds a comment after a name, one after the `(` and one holding a `)`, but none holding a comma, though the pattern's comment (sprint.py:1126) says each comment is taken whole to its line's end; RULINGS: Round-one findings, judged on d2e053af through the plan in throwaway fixtures. "mid-merge the list names a conflicted module once per index stage" CLOSED: with `tests/test_tool_import.py` at three index stages the plan prints the AC1 line exactly, and my set-kept, sort-dropped mutant fails 11 tests. "the file-name pattern backtracks" CLOSED: `a.tool.py`, `b.ool.py` and `c.my-ool.py` list nothing for `scripts/ool.py`, while a lone `build/ool.py` and `--file=tool.py` are still read. "a comment inside a parenthesised from-import hides the next name" CLOSED in the shipped code (a comment after a name, after the `(`, holding a `)`, or holding a comma all read correctly at HEAD), with its comma case unpinned as the ISSUES finding says. "a module under a directory the unit declares is listed as outside its Affects" CLOSED: `tests/` covers `tests/deep/test_tool_deep.py`, the declared prefix `tests/test_tool` covers nothing, and my direct-children-only mutant is killed. "the changelog's repository figure is wrong at its own commit" CLOSED: the count is gone, and each new changelog, docstring and reference sentence holds when run (a logging git wrapper sees one test-module listing per plan for a two-unit batch, human and JSON). "the one-left-out boundary of the cap is unpinned" CLOSED: `if rest > 1` is now killed, and HEAD prints `, +1 more (--format json lists all)` for eleven modules. "the header-once rule is unpinned across units" CLOSED: the per-unit header mutant is now killed. The builder's claims hold: all 20 replayed author mutants are killed, the unsorted survivor is killed now that the listing is a set, and the 20 s-bounded unclosed-list test exists. The scan took 0.19 to 0.27 s over 686 tracked modules here (machine-dependent, so the 0.38 and 0.40 s figures are taken on trust). AC1 to AC6, and AC2 under `sprint.affects_check: block`, give the criteria's exact lines and JSON. Against the base ref the rest of the human plan, stderr and JSON (timestamps aside) are identical and every exit code is 0 in 14 fixtures, including the block, warn and off modes. test\_sprint.py passes in full (874), and the verify\_ac dry run reads 6 of 6. The sprint.py hunks in `_close_reconcile` and `_apply_signoff_tail` between the two commits belong to 7d003c053 (BG1551 and BG1552), not this unit, and were not judged here.

## Steps to Reproduce

1. Read the round 2 REJECT of US1326 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1326 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] a comment holding a comma inside a parenthesised import list is unpinned (sprint.py:1134, sprint.py:1176): narrowing `_REACH_COMMENT` from `#[^\n]*` to `#[^\n,]*`, so a comment is cut at its first comma, survives all 18 PlanTestModuleAdvisoryTests (18 passed). Run through `sprint.py plan --stories Ready --no-fetch --skip-personas` in a fixture, that mutant drops a module holding `from lib import (  # noqa: E402, F401` and `surface,` for a declared `scripts/lib/surface.py`, which brings round one's defect back for the commonest comment an import list carries, and it lists a module whose only `surface` stands in the comment `# see a, surface`. HEAD lists the first and not the second, so the code is right and only the pin is missing: the new test (test\_sprint.py:2590) holds a comment after a name, one after the `(` and one holding a `)`, but none holding a comma, though the pattern's comment (sprint.py:1126) says each comment is taken whole to its line's end
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** US1326 AC1 still passes: The plan lists each test module outside a unit's Affects that imports or runs a script it declares
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_the_plan_lists_test_modules_that_import_or_run_a_declared_script
  - **Verified:** yes (2026-11-23)
- [ ] **AC3** US1326 AC2 still passes: The list rides beside the registry advice and refuses nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_the_list_rides_beside_the_registry_advice_and_refuses_nothing
  - **Verified:** yes (2026-11-23)
- [ ] **AC4** US1326 AC3 still passes: A test module the unit already declares is not listed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_a_test_module_in_the_units_affects_is_not_listed
  - **Verified:** yes (2026-11-23)
- [ ] **AC5** US1326 AC4 still passes: A unit that declares no script, or a script no test reaches, prints nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_a_unit_with_no_script_or_no_reaching_test_prints_nothing
  - **Verified:** yes (2026-11-23)
- [ ] **AC6** US1326 AC5 still passes: Only the project's own tracked test modules are read
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_only_the_projects_own_tracked_test_modules_are_read
  - **Verified:** yes (2026-11-23)
- [ ] **AC7** US1326 AC6 still passes: A script many test modules reach is listed to a cap, with the rest counted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_a_script_many_modules_reach_is_listed_to_a_cap
  - **Verified:** yes (2026-11-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
