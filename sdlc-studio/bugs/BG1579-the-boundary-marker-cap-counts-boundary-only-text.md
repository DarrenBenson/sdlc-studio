# BG1579: The boundary-marker cap counts @boundary_only text inside fixture strings as marked tests, so BG1519's fixtures pushed it over six

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/tests/test_boundary_marker.py
> **Evidence:** Push gate on devserver1, 2026-11-18, log boundary-suite-last.log line 233.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T03:04:05Z

## Summary

`_marked()` in tools/tests/`test_boundary_marker.py` finds every `@boundary_only(...)` by regex over each test file's text, so a decorator written inside a string literal (a fixture module a test writes to disk) counts as a marked test. BG1519 (run sixteen) added three such fixtures to `test_gate.py`; the count reached 7 against the cap of 6 and the push boundary refused commit 3777e27e. Four tests are really marked.

## Steps to Reproduce

python3 -m pytest tools/tests/`test_boundary_marker.py`::TheMarkerIsHonoured::`test_the_marked_set_stays_small_and_named` at 3777e27e.

## Proposed Fix

Read decorators from the AST of each module's functions, so only a real decorated test counts.

## Acceptance Criteria

- [ ] **AC1** Given test_gate.py's fixture modules that write `@boundary_only(...)` inside string literals, when `_marked()` scans the shipped test tree, then it lists only decorators applied to real test functions, so the marked-set cap test passes. Fails on: a decorator inside a string literal counted as a marked test.
  - **Verify:** pytest tools/tests/test_boundary_marker.py::TheMarkerIsHonoured::test_the_marked_set_stays_small_and_named
  - **Verified:** yes (2026-11-18)
- [ ] **AC2** Given a throwaway test module holding one decorated test and one string literal containing the decorator text, when `_marked()` scans it, then it returns exactly the decorated test. Fails on: the string counted, or the real decorator missed.
  - **Verify:** pytest tools/tests/test_boundary_marker.py -k fixture_string
  - **Verified:** yes (2026-11-18)

## Impact

The push is refused for a count no real test raised, and the cap stops meaning the marked set.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
