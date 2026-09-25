# BG0770: CI's unittest run of tools/tests is red on main

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Affects:** tools/tests/test_message_first_gate.py, tools/tests/test_lean_refusal_log.py, tools/tests/test_lean_tmp_hygiene.py, tools/tests/test_lean_ci_unittest_run.py, changelog.d/BG0770.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T10:50:10Z

## Summary

CI's Lint run 36119025214 at a05b1203 failed 16 of 810 tools/tests under 'python3 -m unittest discover -s tools/tests'; the local push gate runs pytest and passed. (1) 14 in `test_message_first_gate`: `test_lean_refusal_log` (BG0761) imports that module's tearDownModule, which deletes the shared `_SCRIPTS_TEMPLATE` after `refusal_log`'s tests but never resets the global, so `test_message_first_gate`'s own fixtures later symlink to a deleted directory and every script lane fails 'can't open file'. Under pytest each file is imported under its own module name, so the global is not shared and it passes. (2) 3 subtests in `test_lean_tmp_hygiene` (BG0753) run pytest with '-n 2', but CI installs pytest without pytest-xdist, so pytest exits 4 on usage.

## Steps to Reproduce

1. `SDLC_STUDIO_BOUNDARY_SUITE`=1 python3 -m unittest discover -s tools/tests from the repo root: 14 FAIL in `test_message_first_gate` (reproduced locally 2026-09-25). 2. In an environment without pytest-xdist, `test_lean_tmp_hygiene`'s -n 2 subtests fail 'usage: pytest.main()' (CI run 36119025214).

## Proposed Fix

Reset `_SCRIPTS_TEMPLATE` to None in `test_message_first_gate.tearDownModule` (or give the importer its own template), and have the tmp-hygiene probe skip its -n 2 variants, named, when xdist is not importable.

## Acceptance Criteria

- [ ] **AC1** Given `python3 -m unittest discover -s tools/tests` run as CI runs it (module order included, `test_lean_refusal_log` before `test_message_first_gate`), then every `test_message_first_gate` test passes. Fails on: HEAD's `tearDownModule`, which deletes the shared scripts template and leaves the module global pointing at it
  - **Verify:** pytest tools/tests/test_lean_ci_unittest_run.py::CiUnittestRunTests::test_the_gate_fixture_survives_an_importers_teardown
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** Given an interpreter where `xdist` cannot be imported, then `test_lean_tmp_hygiene` passes with its `-n 2` variants skipped and named, and where `xdist` imports they still run. Fails on: HEAD, which exits 4 on the `-n` usage error
  - **Verify:** pytest tools/tests/test_lean_ci_unittest_run.py::CiUnittestRunTests::test_the_tmp_probe_skips_worker_runs_without_xdist
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
