# BG1036: BG0978's stub-interpreter test cannot tell sys.executable from the PATH's python3, and checks only an exit code

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_pre_push_stub_unactivated.py, changelog.d/BG0978.md, changelog.d/BG1036.md
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T10:45:18Z

## Summary

From BG0978's round-1 QA review on 2026-10-13 (APPROVE, nothing blocking). (1) tools/tests/`test_pre_push_stub_interpreter.py` puts its venv's bin first on PATH, so `shutil.which("python3")` and `sys.executable` resolve to the same interpreter by construction: a stub that execs the PATH's python3 passes, yet loses the venv when the suite runs as `.venv/bin/python -m pytest` without activation. The docstring's and changelog's 'the interpreter running these tests' is wider than what is pinned. (2) The probe asserts only the stub's exit code; a wrapper that drops "$@" exits 0 and passes this module alone (a sibling hook test kills it). (3) Pre-existing: the suite needs PyYAML by design (CR0207), so 'a contributor whose pytest lives only in a virtualenv can now get a push through' holds for a virtualenv carrying the suite's test dependencies.

## Steps to Reproduce

Change the stub to exec `shutil.which("python3")`; run `test_pre_push_stub_interpreter.py`: green. Run the same probe with the venv not on PATH: the marker import fails.

## Proposed Fix

Run the probe a second time without the venv on PATH, so only sys.executable can find the marker; print the marker's value and assert it; say in the changelog that the virtualenv carries the suite's test dependencies.

## Acceptance Criteria

- [ ] **AC1** Given the stub built under a virtualenv interpreter that is not on PATH, when its python3 imports the virtualenv's marker, then it succeeds and prints the marker's value, and the test fails when the stub execs the PATH's python3
  - **Verify:** pytest tools/tests/test_pre_push_stub_unactivated.py::StubUnactivatedTests::test_stub_path_keeps_an_unactivated_interpreter

## Impact

A later edit could make the stub follow PATH again with this test green, and the release note says slightly more than the suite proves.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): Won't Fix, not beneficial (LL0056): the regression it guards would show as loud red tests, never a false pass |
