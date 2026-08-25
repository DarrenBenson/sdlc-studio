# BG0602: The close checklist enumerates its checks by `_ck_` name prefix

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint_report` gathers the close checklist by scanning its own module namespace for callables whose name starts with `_ck_`. A check renamed, or defined outside that prefix, silently leaves the checklist with no error anywhere - the roster shrinks and the close still reports a clean pass. This is the same shape as the enumeration defects already filed against the edit-verb vocabulary: a list nobody has to update is a list that goes quietly out of date.

## Steps to Reproduce

Read the checklist assembly in `.claude/skills/sdlc-studio/scripts/sprint_report.py` and confirm the roster comes from a name-prefix scan rather than an explicit registry. Rename any `_ck_` function to drop the prefix and run `sprint.py close --dry-run`: the check vanishes from the report and nothing refuses.

## Proposed Fix

Hold the checks in an explicit registry (a module-level tuple, or a decorator that appends), and add a test pinning the roster's length and names so a silent shrink fails. Keep the prefix as a convention if you like, but stop deriving the roster from it.

## Acceptance Criteria

- [ ] **AC1** Given a checklist function renamed so it no longer carries the `_ck_` prefix, when the close runs, then the roster is UNCHANGED or the run refuses naming the missing check - today it vanishes silently and the close still reports a clean pass
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistRegistryTests::test_a_renamed_check_does_not_vanish_from_the_roster
- [ ] **AC2** Given the checklist registry, when the roster test runs, then it asserts the exact NAMES and the count, so adding a check without registering it fails
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistRegistryTests::test_the_roster_pins_names_and_count
- [ ] **AC3** Given a check registered but not defined, when the module loads, then it refuses at import rather than reporting a shorter roster - an absent check and a check nobody wrote must not read the same
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistRegistryTests::test_a_registered_but_undefined_check_refuses_at_import

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Filed |
