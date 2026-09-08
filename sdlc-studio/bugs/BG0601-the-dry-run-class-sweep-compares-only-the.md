# BG0601: The dry-run class sweep compares only the first two probes of each pair

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The parity sweep in `DryRunScratchParityTests` walks 22 probe classes and asserts the scratch and the read root agree, but it slices each probe's result to its first two elements before comparing. A probe whose divergence appears only from the third element on is reported as agreeing. The sweep was written to be the broad safety net under the read-root split, and a net with a two-element horizon is narrower than the thing it guards.

## Steps to Reproduce

In `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py`, find the class sweep in `DryRunScratchParityTests` and the `[:2]` slice applied to each probe's result. Construct a probe whose scratch and read-root results share their first two entries and differ at the third; the sweep passes. Removing the slice fails it. Demonstrated during BG0593's delivery, not hypothesised.

## Proposed Fix

Compare the probes in full, or state a bounded reason for the horizon in the test's own docstring so the next reader knows the sweep is partial. If a full comparison is too noisy, sort and compare as sets rather than truncating - truncation silently exempts the tail.

## Acceptance Criteria

- [ ] **AC1** Given a SYNTHETIC `_ck_` probe registered on the module for the duration of the test, whose real-tree and preview answers agree on `state` and `value` and differ in `detail`, when the dry-run parity sweep runs, then it FAILS and names that probe. Measured, no shipped probe diverges that way today - the full-width sweep reports zero differing across all of them - so the case has to be constructed rather than found, and constructing it is what shows the sweep can see the third field. Every `_ck_` resolver returns `(state, value, detail)`, so today's `[:2]` compares `(state, value)` while the fixture's own comment says it compares `(state, detail)` - a probe that reads the scratch and differs only in WHY is read as agreeing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_a_difference_in_the_detail_field_is_caught
  - **Verified:** no
- [ ] **AC2** Given every `_ck_` probe against an unmodified tree, when the sweep runs, then it PASSES - the paired control, because a sweep that fails on correct output is one that gets deleted rather than fixed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_the_sweep_passes_on_an_unmodified_tree
  - **Verified:** no
- [ ] **AC3** Given a `_ck_` resolver added to the module after the sweep's code was written, when the sweep runs, then it is swept too, because the roster is resolved from the module at run time rather than listed. An enumerated roster exempts whichever probe is added next, which is the shape this repository keeps meeting, and the sensitivity control cannot serve as the third row: measured, the blind scratch already differs from the real tree at the `state` field, so narrowing that control leaves it discriminating
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_the_sensitivity_control_compares_what_the_sweep_compares
  - **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, narrow the swept comparison back to `fn(real)[:2]` against `fn(copy)[:2]`, dropping the detail field | Given a SYNTHETIC `_ck_` probe registered on the module for the duration of the test, whose real-tree and preview answers agree on `state` and `value` and differ in `detail`, when the dry-run parity sweep runs, then it FAILS and names that probe. Measured, no shipped probe diverges that way today - the full-width sweep reports zero differing across all of them - so the case has to be constructed rather than found, and constructing it is what shows the sweep can see the third field. Every `_ck_` resolver returns `(state, value, detail)`, so today's `[:2]` compares `(state, value)` while the fixture's own comment says it compares `(state, detail)` - a probe that reads the scratch and differs only in WHY is read as agreeing |
| AC2 | in .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, swap the sweep's preview side for the BLIND scratch, so every probe reading outside `sdlc-studio/` differs and the sweep fails on a correct tree | Given every `_ck_` probe against an unmodified tree, when the sweep runs, then it PASSES - the paired control, because a sweep that fails on correct output is one that gets deleted rather than fixed |
| AC3 | in .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, hard-code the probe roster as a literal tuple instead of reading it off the module | Given a `_ck_` resolver added to the module after the sweep's code was written, when the sweep runs, then it is swept too, because the roster is resolved from the module at run time rather than listed. An enumerated roster exempts whichever probe is added next, which is the shape this repository keeps meeting, and the sensitivity control cannot serve as the third row: measured, the blind scratch already differs from the real tree at the `state` field, so narrowing that control leaves it discriminating |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Filed |
