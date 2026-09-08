# BG0567: the upgrading-project baseline compares against this tree minus one branch, not against the base ref, so a regression the epic introduced elsewhere sits on both sides and is invisible

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** Round-3 delivery review of RUN-01KZM49Y, 2026-08-10. US0663 AC2 originally demanded a baseline captured from the base ref before the epic's branch existed. `_capture_with_softening_disabled` clones the CURRENT skill tree and disables one branch, so every other change the epic made is present on both sides of the comparison. The seat also noted the baseline fixture holds 0 retros while the case under test holds 3, so it is not literally the same fixture either. The criterion was narrowed to describe what is built rather than left overstating it.
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A counterfactual baseline is only as good as what it holds constant. Disabling one branch in the current tree answers `did THIS branch change the behaviour`, which is a real question and the one the test now claims to ask. It does not answer `is an upgrading project's behaviour what it was before this epic`, which is what the unit promises a consuming project.

The difference matters for exactly the population the promise is about. An established project upgrading to v5 gets whatever this epic did to the transition ladder, not merely whatever the softening branch did. A change elsewhere in the epic - to the advisory, to the gate ordering, to a message - is invisible to a comparison that carries it on both sides.

The stronger form is buildable: capture the baseline by checking the base ref out into a throwaway worktree and running the same fixture against it. It costs a worktree per assertion, which is why it was not built under time pressure, and that is a reason to file it rather than to claim it.

## Steps to Reproduce

1. Read `_capture_with_softening_disabled` in `test_transition.py`: it clones the current skill tree and rewrites one branch. 2. Introduce any other behaviour change in the same epic - a changed message on the transition path, say. 3. The upgrading-project test still passes, because the change is present in both the baseline and the observed run.

## Proposed Fix

Capture from the BASE REF: `git worktree add` a throwaway checkout of the run's base ref, run the same fixture against its `transition.py`, and compare. Use one fixture shape for both sides so the comparison is like for like - the current baseline holds 0 retros against the observed 3. Pin it by introducing a deliberate unrelated change on the epic's side and asserting the comparison notices, which the present form does not.

## Acceptance Criteria

- [ ] **AC1** Given the upgrading-project rehearsal, when its baseline is captured, then it comes from a PINNED commit named as a constant in the test - the last commit before the softening epic - extracted read-only with `git archive` piped through `tar`, rather than from the current tree with one branch rewritten. `git worktree add` is deliberately not used: it mutates git administrative state from inside a test that ships to consuming projects, and leaves entries behind when the test dies. A regression the epic introduced anywhere else in the skill tree then differs between the two sides instead of sitting on both. "The run's base ref" is not usable here: the epic landed in August, so this run's base ref already contains it and the comparison would run the tree against itself
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::UpgradeBaselineTests::test_the_baseline_comes_from_the_pinned_pre_epic_commit
  - **Verified:** no
- [ ] **AC2** Given both sides of the comparison, when their fixtures are built, then the test asserts both sides receive the SAME ARGUMENTS, not merely that their outputs match. Measured against the pinned tree, the baseline's output is byte-identical for a fixture with retros and one without, because the softening is the only thing that reads them and the pinned tree has none - so an output comparison survives a changed argument and only an assertion on the call shape catches it. Both callers are covered, including the dormant-gate one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::UpgradeBaselineTests::test_both_sides_run_the_same_fixture_shape
  - **Verified:** no
- [ ] **AC3** Given a deliberate change on the epic's side OUTSIDE the softening branch, when the comparison runs, then it FAILS - proving it sees more than the one branch the old baseline disabled
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::UpgradeBaselineTests::test_a_regression_outside_the_branch_is_reported
  - **Verified:** no
- [ ] **AC4** Given no change at all beyond the epic itself, when the comparison runs, then it PASSES. This is the control AC1 and AC3 cannot supply between them: a comparison that is permanently red satisfies both. Measured, no compared string in any of the four fixture shapes carries a run id or a temporary path, so the existing normalisation is dead on this comparison and cannot be what the control turns on - the pin itself is
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::UpgradeBaselineTests::test_an_unchanged_tree_compares_equal
  - **Verified:** no
- [ ] **AC5** Given a root where the pinned commit cannot be resolved - a consuming project's installed copy, a shallow clone, or no git at all - when the test runs, then it SKIPS naming that reason rather than erroring. `install.sh` copies the skill tree wholesale, tests included, so this ships to projects with none of that history, and a test that breaks there is one consumers delete
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::UpgradeBaselineTests::test_an_unresolvable_pin_skips_with_its_reason
  - **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/tests/test_transition.py, revert `_capture_with_softening_disabled` to copying the current tree and rewriting the softening marker | Given the upgrading-project rehearsal, when its baseline is captured, then it comes from a PINNED commit named as a constant in the test - the last commit before the softening epic - extracted read-only with `git archive` piped through `tar`, rather than from the current tree with one branch rewritten. `git worktree add` is deliberately not used: it mutates git administrative state from inside a test that ships to consuming projects, and leaves entries behind when the test dies. A regression the epic introduced anywhere else in the skill tree then differs between the two sides instead of sitting on both. "The run's base ref" is not usable here: the epic landed in August, so this run's base ref already contains it and the comparison would run the tree against itself |
| AC2 | in .claude/skills/sdlc-studio/scripts/tests/test_transition.py, change the `retros` argument the baseline side passes to `_proj` | Given both sides of the comparison, when their fixtures are built, then the test asserts both sides receive the SAME ARGUMENTS, not merely that their outputs match. Measured against the pinned tree, the baseline's output is byte-identical for a fixture with retros and one without, because the softening is the only thing that reads them and the pinned tree has none - so an output comparison survives a changed argument and only an assertion on the call shape catches it. Both callers are covered, including the dormant-gate one |
| AC3 | in .claude/skills/sdlc-studio/scripts/tests/test_transition.py, narrow the compared output to the lines the softening branch itself emits | Given a deliberate change on the epic's side OUTSIDE the softening branch, when the comparison runs, then it FAILS - proving it sees more than the one branch the old baseline disabled |
| AC4 | in .claude/skills/sdlc-studio/scripts/tests/test_transition.py, move the pinned constant forward to a commit that already contains the softening epic | Given no change at all beyond the epic itself, when the comparison runs, then it PASSES. This is the control AC1 and AC3 cannot supply between them: a comparison that is permanently red satisfies both. Measured, no compared string in any of the four fixture shapes carries a run id or a temporary path, so the existing normalisation is dead on this comparison and cannot be what the control turns on - the pin itself is |
| AC5 | in .claude/skills/sdlc-studio/scripts/tests/test_transition.py, delete the resolvability check so an unresolvable pin raises | Given a root where the pinned commit cannot be resolved - a consuming project's installed copy, a shallow clone, or no git at all - when the test runs, then it SKIPS naming that reason rather than erroring. `install.sh` copies the skill tree wholesale, tests included, so this ships to projects with none of that history, and a test that breaks there is one consumers delete |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Filed |
