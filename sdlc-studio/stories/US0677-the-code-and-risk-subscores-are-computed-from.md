# US0677: The code and risk subscores are computed from the hunks a unit CHANGES against the base ref, not from every function in every declared file

> **Status:** Draft
> **Delivers:** CR0549
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/tests/test_complexity.py, .claude/skills/sdlc-studio/scripts/complexity.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py
> **Epic:** EP0217
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The code and risk subscores are computed from the hunks a unit CHANGES against the base ref, not from every function in every declared file
**So that** CR0549 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given the DECLARED basis, when `route.estimate` scores a unit, then `code` and `risk` are computed from the unit's own `Points` and `Affects` breadth and NOT from a complexity read over whole declared files - measured over this corpus that moves `light` from 13% to 33% while whole-file complexity leaves it at 13%
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DeclaredBasisTests::test_the_declared_score_reads_points_and_affects_not_whole_files
- [ ] **AC2** Given the SAME production file declared by two units, one at one point and one at eight, when both are scored on the declared basis, then they band DIFFERENTLY - the discrimination is the whole request, and whole-file complexity cannot produce it because it never sees the change
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DeclaredBasisTests::test_one_file_two_sizes_two_bands
- [ ] **AC3** Given the DIFF basis, when `route.estimate` scores a unit, then `code` is computed from the hunks that unit changes and `risk` is left FILE-level and says so in the returned dict - churn counts commits touching a file, so a two-line change and a rewrite carry identical churn and a per-hunk risk is not a quantity that exists
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DiffBasisTests::test_code_is_hunk_scoped_and_risk_declares_itself_file_level
- [ ] **AC4** Given a run whose base ref names changes across several units, when one unit's diff basis is computed, then the changed lines are INTERSECTED with that unit's own `Affects` before scoring - without it every unit in a multi-unit run scores identically, which is a new constant reached by a different road
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DiffBasisTests::test_the_run_diff_is_intersected_with_the_units_own_affects
- [ ] **AC5** Given a hunk that maps to no enclosing function - an import, module-level code, a deleted block - when it is scored, then it is counted by a stated rule rather than dropped, because that is the common case for the small change AC2 is about
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_complexity.py::HunkMappingTests::test_a_hunk_outside_any_function_is_counted_by_a_stated_rule

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |

| 2026-08-24 | sdlc-studio | RE-GROOMED against CR0549's second and third corrections after a pre-code goal review REJECTED the first attempt: the declared basis now reads `Points` and `Affects` breadth rather than whole-file complexity, measured to move `light` from 13% to 33%. |
