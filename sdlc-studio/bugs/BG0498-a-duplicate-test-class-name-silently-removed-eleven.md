# BG0498: a duplicate test class name silently removed eleven tests from the suite

> **Status:** Fixed
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, tools/tests/test_test_census.py
> **Verification depth:** functional (all 11 shadowed tests collected and passing after the rename; the new guard KILLED by a planted duplicate in the skills suite and green on the clean tree)
> **Severity:** High
> **Points:** 2

## Summary

US0609 added a second `class FileAndCloseTests` to `test_sprint.py`, at line 11991, while one already existed at line 4313. Python does not complain - the second definition simply replaces the first - so the ELEVEN tests on the earlier class stopped being collected. The suite stayed green; the count just went down, and nobody was watching the number.

The damage was visible for hours and misread. `US0282` and `US0283` were reported non-conformant with `verifier exited 0 but ran NO tests - a filter that matches nothing (renamed or deleted test, stale -k/-run pattern)`. The named tests were all still in the file. The diagnosis the message offers - a stale selector - is the wrong one here, and the right one is that the class holding them no longer exists at runtime.

The eleven: `test_blocked_close_offers_file_and_close`, `test_file_and_close_records_linked_artefacts_and_outcome`, `test_file_and_close_names_deferrals_in_retro_and_anchor`, `test_a_run_stopped_mid_flight_can_still_file_and_close`, `test_a_completed_close_still_refuses_a_second_filing`, `test_a_run_that_already_filed_refuses_whatever_its_outcome`, `test_hard_correctness_gate_refuses_file_and_close`, `test_file_and_close_refuses_a_rerun_and_duplicates_nothing`, `test_file_and_close_refuses_a_goal_less_run`, `test_close_presents_pending_decisions_at_the_stop`, `test_reclose_reports_outstanding_set_trend.` All eleven pass once the shadow is removed.

## Steps to Reproduce

1. `grep -n '^class FileAndCloseTests' test_sprint.py` -> two definitions.
2. `pytest test_sprint.py --collect-only -q | grep -c FileAndCloseTests` -> 3, not 14.
3. `verify_ac run --id US0282` -> every AC reports 'ran NO tests' though the tests are in the file.

## Proposed Fix

Repaired here: the second class is renamed `CadenceDebtFileAndCloseTests`, which is what it actually covers, and all eleven tests return and pass. Guarded by a new AST check over both suite directories that refuses any test module defining a module-level class name twice - parsed rather than grepped, because a grep cannot tell a definition from a mention.

## Impact

Eleven tests silently left the suite and the gate reported green throughout. That is the worst shape a test defect takes: the coverage is gone, nothing says so, and the only symptom - two units' verifiers finding no tests - carries a message that points at the wrong cause. The file-and-close bounded exit, which those eleven cover, is a correctness path; it went unexercised for the rest of the run.

## Acceptance Criteria

### AC1: no test module defines a class name twice

- **Then** an AST sweep over both suite directories reports no module-level class name defined
  more than once, so a second definition cannot silently replace the first
- **Verify:** pytest tools/tests/test_test_census.py::DuplicateTestClassTests::test_no_test_module_defines_a_class_name_twice
- **Verified:** yes (2026-08-02)

### AC2: the detector's premise is sound

- **Then** two module-level class definitions of one name are both present in the parsed AST,
  so the guard is reading a real signal rather than passing over a clean tree by accident
- **Verify:** pytest tools/tests/test_test_census.py::DuplicateTestClassTests::test_the_guard_sees_a_planted_duplicate
- **Verified:** yes (2026-08-02)

### AC3: the eleven shadowed tests run again

- **Then** `FileAndCloseTests` collects its full set rather than the three the shadow left
- **Verify:** shell python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py --collect-only -q | grep -c "FileAndCloseTests::" | grep -qE "^1[0-9]$"
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
