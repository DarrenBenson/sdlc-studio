# BG1040: gate_prereqs prints the SDLC_COVERAGE_PYTHON route without reading that interpreter, reads markers without evaluating them, and skips -r lines silently

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/gate_prereqs.py, tools/tests/test_gate_prereqs_followup.py, changelog.d/US1003.md, changelog.d/BG1040.md, tools/tests/test_gate_prereqs.py
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T13:59:29Z

## Summary

From US1003's round-2 QA review on 2026-10-13 (APPROVE, nothing blocking). (1) `_other_route` always prints `<override> -m pip install 'coverage>=7.10'` and never asks whether that interpreter has pip or is externally managed, so for a `venv --without-pip` or a managed pip-less override the route fails with 'No module named pip'; the changelog's 'the route works on the interpreter that lacks the package' over-claims there. (2) The parser reads environment markers but does not evaluate them, so a requirement whose marker is false here is reported missing; and a `-r more.txt` line is skipped with every distribution it includes, unnamed, though the changelog says the checker names any line it cannot read. (3) 'An upper bound sets no floor' has no test that fails: reading every specifier as a floor survives, because the only upper-bound fixture is too old on both bounds. (4) The override pin is live only where the test runner has coverage itself.

## Steps to Reproduce

Set `SDLC_COVERAGE_PYTHON` to a `venv --without-pip` interpreter without coverage and run `python3 tools/gate_prereqs.py check`: the route offered fails. Declare `zzq-absent-dist; python_version < "3"`: reported missing.

## Proposed Fix

Read the override's route from the override (run the same probe as `install_route` there); evaluate markers with the stdlib or name them unevaluated; follow or name `-r` lines; add an upper-bound fixture that meets its floor; give the override pin a fake coverage distribution so it holds on any runner.

## Acceptance Criteria

- [ ] **AC1** Given `SDLC_COVERAGE_PYTHON` naming a virtual environment with no pip and no coverage, when the check runs, then the route it gives is one that interpreter can run
  - **Verify:** pytest tools/tests/test_gate_prereqs_followup.py::FollowupTests::test_the_override_route_is_read_from_the_override
- [ ] **AC2** Given a requirement whose marker is false on this interpreter, and a `-r` line, when the check runs, then the first is not reported missing and the second is followed or named
  - **Verify:** pytest tools/tests/test_gate_prereqs_followup.py::FollowupTests::test_markers_and_r_lines_are_not_misread
- [ ] **AC3** Given `coverage>=7.10,<8` and coverage 7.15 installed, when the check runs, then no gap is reported
  - **Verify:** pytest tools/tests/test_gate_prereqs_followup.py::FollowupTests::test_an_upper_bound_sets_no_floor

## Impact

Low: each case is uncommon, and the shipped requirements-dev.txt has neither markers nor -r lines; the advice is wrong rather than the gate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
