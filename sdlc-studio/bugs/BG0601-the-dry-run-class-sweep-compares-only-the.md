# BG0601: The dry-run class sweep compares only the first two probes of each pair

> **Status:** Fixed
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

- [x] **AC1** Given a SYNTHETIC `_ck_` probe registered on the module for the duration of the test, whose real-tree and preview answers agree on `state` and `value` and differ in `detail`, when the dry-run parity sweep runs, then it FAILS and names that probe. Measured, no shipped probe diverges that way today - the full-width sweep reports zero differing across all of them - so the case has to be constructed rather than found, and constructing it is what shows the sweep can see the third field. Every `_ck_` resolver returns `(state, value, detail)`, so today's `[:2]` compares `(state, value)` while the fixture's own comment says it compares `(state, detail)` - a probe that reads the scratch and differs only in WHY is read as agreeing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_a_difference_in_the_detail_field_is_caught
  - **Verified:** yes (2026-09-09)
- [x] **AC2** Given every `_ck_` probe against an unmodified tree, when the sweep runs, then it PASSES - the paired control, because a sweep that fails on correct output is one that gets deleted rather than fixed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_the_sweep_passes_on_an_unmodified_tree
  - **Verified:** yes (2026-09-09)
- [x] **AC3** Given a `_ck_` resolver added to the module after the sweep's code was written, when the sweep runs, then it is swept too, because the roster is resolved from the module at run time rather than listed. An enumerated roster exempts whichever probe is added next, which is the shape this repository keeps meeting, and the sensitivity control cannot serve as the third row: measured, the blind scratch already differs from the real tree at the `state` field, so narrowing that control leaves it discriminating
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_a_resolver_added_after_the_sweep_is_swept_too
  - **Verified:** yes (2026-09-09)

- [ ] **AC4** Given the sweep, when it runs, then it goes through the SAME comparison its own criteria drive rather than a second copy of it. Asserted by behaviour, not by reading the source: the sweep is run with the shared helper spied on and has to have gone through it. No other row here can see this - every criterion above drives the helper, so a sweep carrying its own walk leaves them pinning the copy and the sweep pinned by nothing, which is how the whole delivery reverted with all eleven of them green
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_the_sweep_goes_through_the_same_comparison_its_criteria_do

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, narrow the swept comparison back to `fn(real)[:2]` against `fn(copy)[:2]`, dropping the detail field | Given a SYNTHETIC `_ck_` probe registered on the module for the duration of the test, whose real-tree and preview answers agree on `state` and `value` and differ in `detail`, when the dry-run parity sweep runs, then it FAILS and names that probe. Measured, no shipped probe diverges that way today - the full-width sweep reports zero differing across all of them - so the case has to be constructed rather than found, and constructing it is what shows the sweep can see the third field. Every `_ck_` resolver returns `(state, value, detail)`, so today's `[:2]` compares `(state, value)` while the fixture's own comment says it compares `(state, detail)` - a probe that reads the scratch and differs only in WHY is read as agreeing |
| AC2 | in .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, swap the sweep's preview side for the BLIND scratch, so every probe reading outside `sdlc-studio/` differs and the sweep fails on a correct tree | Given every `_ck_` probe against an unmodified tree, when the sweep runs, then it PASSES - the paired control, because a sweep that fails on correct output is one that gets deleted rather than fixed |
| AC3 | in .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, hard-code the probe roster as a literal tuple instead of reading it off the module | Given a `_ck_` resolver added to the module after the sweep's code was written, when the sweep runs, then it is swept too, because the roster is resolved from the module at run time rather than listed. An enumerated roster exempts whichever probe is added next, which is the shape this repository keeps meeting, and the sensitivity control cannot serve as the third row: measured, the blind scratch already differs from the real tree at the `state` field, so narrowing that control leaves it discriminating |

| AC4 | in .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, restore the sweep's own roster walk and comparison loop in place of the shared helper call | Given the sweep, when it runs, then it goes through the SAME comparison its own criteria drive rather than a second copy of it |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Filed |
| 2026-09-09 | Claude Fable 5.1 | Delivered in 681021cc. The sweep's comparisons widened from a two-field slice to the resolver's whole return, and the roster resolved from the module at run time rather than listed. Three criteria, three mutants killed |
| 2026-09-10 | Claude Opus 5 | Delivery review, all three seats REJECT on one finding, and it was right: the three criteria drove `_parity`, a helper the delivery ADDED, while the sweep kept its own roster walk and its own comparison. Reverting the sweep's two-field slices left all eleven tests in the class green, so the whole delivery was revertible with its own criteria passing. Verified by hand before acting on it. The width is now decided in ONE place, `_answer`, which the sweep and the helper both call, and the sweep calls the helper rather than walking the roster a second time. Two mutants, both killed: narrowing the width reddens AC1, re-inlining the sweep's copy reddens the new AC4. That second row exists because this class had already shipped the private-copy shape once, and a comment forbidding it was the only thing standing against a repeat - a rule with no gate behind it |
