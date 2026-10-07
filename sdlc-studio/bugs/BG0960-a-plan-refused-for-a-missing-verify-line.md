# BG0960: A plan refused for a missing Verify line tells you to add Affects and Points

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0960.md
> **Evidence:** Field report, 2026-10-07, sprint plan on sdlc-studio-lens. BG-01M46B27 already declared Affects and Points. The refusal named the missing Verify line, then the fix block printed only the Affects and Points templates.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Grok 4.7; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T08:40:54Z

## Summary

sprint plan refuses an ungroomed unit and then prints one fix block, `BREAKDOWN_FIX`, which always shows how to add Affects and Points. That block is right when those fields are missing. When the unit already has both and was refused because no criterion carries a Verify line or a manual marker (`ac_why` no-verifier), the same block is the wrong repair: it does not mention Verify. The specific sentence above the block does name the missing verifier, and then the fix you are told to apply does not.

## Steps to Reproduce

1. Take a bug that has Affects, Points and authored acceptance criteria, and no Verify line. 2. sprint.py plan that one unit. 3. The refusal names the missing verifier and then prints the Affects and Points templates as the fix.

## Proposed Fix

Print the repair that matches the miss. A missing Affects or Points keeps today's field template. A no-verifier miss shows a Verify line (or a manual marker) and does not tell the author to add fields the unit already has.

## Acceptance Criteria

- [ ] **AC1** Refusing a unit that already has Affects and Points but no verifier names a Verify line as the fix
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BreakdownGateTests::test_the_refusal_names_the_unit_what_it_lacks_and_the_fix_for_a_missing_verifier
- [ ] **AC2** A unit missing Affects or Points still gets today's field template, and a batch holding both kinds of miss shows both repairs, each once
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BreakdownGateTests::test_each_kind_of_miss_gets_its_own_repair
- [ ] **AC3** `sprint.py breakdown`, which prints the same fix block, shows the same matched repair for a no-verifier unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BreakdownGateTests::test_breakdown_prints_the_verify_repair_for_a_no_verifier_unit

## Triage

- Reproduced at fb1ce886 by the code path and by observation: on 2026-10-06 `sprint.py breakdown` refused BG0946, BG0947 and BG0948 for carrying no Verify line and printed the Affects and Points templates as the fix. Already in the code since 2353eee9 (2026-07-15).
- `breakdown` and `plan` share `_breakdown_fix`, so one change repairs both; AC3 holds the second path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Grok 4.7 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Groomed: reproduced at fb1ce886 (`_breakdown_fix` always formats `BREAKDOWN_FIX`), and observed in this session when `sprint.py breakdown` refused BG0946-BG0948 for missing Verify lines and printed the Affects and Points templates; a positive control and the breakdown path added; changelog fragment added to Affects |
