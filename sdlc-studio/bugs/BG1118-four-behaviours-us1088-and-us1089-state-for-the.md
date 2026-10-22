# BG1118: Four behaviours US1088 and US1089 state for the self-check record and gate are pinned by no test: a restored diff admitted by an older row, the record matched to its own unit, the setting read case-insensitively, and an uncovered first fragment refused

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_gate_cases.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py, changelog.d/BG1118.md
> **Evidence:** US1089 QA review, qa-seat-US1089-r1, 2026-10-22, at 69951ff0: [new] finding 2.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T08:09:58Z

## Summary

US1089's QA review (APPROVE, round 1, 2026-10-22) ran 23 mutants; three survived all six of the unit's tests and each changes behaviour when run alone. (a) Comparing only the last row (critic.py:2835) refuses a diff restored to an earlier recorded state, which changelog.d/US1089.md, reference-review.md:489 and the `self_check_gap` docstring say is admitted. (b) Dropping the unit filter (critic.py:2831) lets another unit's row with the same digest admit the brief, because every fixture holds rows of one unit only. (c) Dropping `.lower()` (critic.py:2819) refuses `BLOCK` as unknown, which the commit message says was exercised.

## Steps to Reproduce

Apply any one of the three mutants above and run tests/`test_critic_self_check_refusal.py`: green.

## Proposed Fix

Add the three cases in a new module beside tests/`test_critic_self_check_refusal.py`, reusing its fixture: a record, an edit, a second record, the edit reverted (admitted); a fixture holding another unit's row with the matching digest (refused); `BLOCK` and `Report` (read as block and report).

## Acceptance Criteria

- [ ] **AC1** Given a record, then an edit and a second record, when the edit is reverted, then the brief under block is admitted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_gate_cases.py::GateCaseTests::test_a_restored_diff_is_admitted_by_its_earlier_row
- [ ] **AC2** Given only another unit's row whose digest matches this unit's Affects, then the brief under block is refused
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_gate_cases.py::GateCaseTests::test_another_units_row_does_not_admit
- [ ] **AC3** Given the setting written `BLOCK` or `Report`, then it is read as block or report, not refused as unknown
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_gate_cases.py::GateCaseTests::test_the_setting_is_read_case_insensitively
- [ ] **AC4** Given a unit declaring two changelog fragments whose claims cover only the second, when its self-check is recorded, then it is refused naming the first (US1088's round-2 QA review: narrowing the skip check at critic.py:2754 to `fragments[-1:]` survives, because the two-fragment subtest leaves only the last uncovered)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_gate_cases.py::GateCaseTests::test_an_uncovered_first_fragment_is_refused

## Impact

Each stated behaviour can regress with the suite green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
| 2026-10-22 | sdlc-studio | Retitled: was 'Three behaviours US1089 states for the self-check gate are pinned by no test: a restored diff admitted by an older row, the record matched to its own unit, and the setting read case-insensitively' |
| 2026-10-22 | sdlc | AC4 from US1088's round-2 QA review: an uncovered FIRST fragment is unpinned |
