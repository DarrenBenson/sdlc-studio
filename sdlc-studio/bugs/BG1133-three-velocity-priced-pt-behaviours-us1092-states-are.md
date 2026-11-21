# BG1133: Three VELOCITY Priced/pt behaviours US1092 states are pinned by no test: the Source guard, an earlier row keeping its recorded figure, and rows with no Source named in the rate's basis

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_velocity_priced_cell_rules.py, changelog.d/BG1133.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** US1092 QA review, qa-seat-US1092-r1, 2026-10-26, at a8b90201: surviving mutants 1-3.
> **Created:** 2026-10-26
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-26T14:52:35Z

## Summary

US1092's QA review (APPROVE, 2026-10-26). Surviving mutants: (1) removing the Source guard in `record_velocity` (retro.py:2936) writes Priced/pt 3,846 beside a per-unit Actual of 1,234, against the changelog's 'written only under the Source of the harness capture that formed it'; (2) writing Priced/pt only for the row being updated (retro.py:2965) wipes an earlier row's recorded figure, though 'every earlier row keeps its cells' is stated; (3) dropping rows with no Source from `sources` (retro.py:2489-2490) survives 1,084 tests though the live VELOCITY.md has such rows. The shipped code is correct in each.

## Steps to Reproduce

Apply any one of the three mutants and run `test_velocity_priced_basis`, `test_retro` and `test_sprint`: green.

## Proposed Fix

One test per behaviour in a new module, with fixtures: a per-unit batch Source beside a harness capture; two priced rows, then an update to the second; a row with an empty Source in the pooled rate.

## Acceptance Criteria

- [ ] **AC1** Given a per-unit batch Source, then no Priced/pt is written beside it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_velocity_priced_cell_rules.py::PricedCellRulesTests::test_a_per_unit_source_gets_no_priced_cell
- [ ] **AC2** Given two rows with a recorded Priced/pt, when the second is updated, then the first keeps its figure
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_velocity_priced_cell_rules.py::PricedCellRulesTests::test_an_earlier_rows_priced_figure_survives_an_update
- [ ] **AC3** Given a row with an empty Source among the pooled rows, then the rate's basis names it as unrecorded
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_velocity_priced_cell_rules.py::PricedCellRulesTests::test_an_unrecorded_source_is_named_in_the_basis

## Impact

Three stated behaviours of the VELOCITY row can regress with the suite green.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. US1092's Priced/pt rules behave as stated; three of them are pinned by no test. Test gap only. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-26 | Claude Opus 5.5 | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
