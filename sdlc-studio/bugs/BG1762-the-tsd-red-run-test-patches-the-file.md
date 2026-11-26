# BG1762: The TSD red-run test patches the `file_finding` module it imported, so under the full suite `gate.red_run` files through another copy and the test fails

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_specs_v65.py, changelog.d/BG1762.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-25T23:44:44Z

## Summary

`tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_tsd_names_the_authors_mutants_and_the_red_run_policy` patches `file_finding.file_finding` on the module object it imported at load (`mock.patch.object(file_finding, ...)`). `gate.red_run` imports `file_finding` lazily, at call time, from `sys.modules`. When an earlier test in the same worker has replaced `sys.modules['file_finding']`, gate files through the unpatched copy: the real filer allocates BG0002 in the fixture, so the earlier assertions still pass, and `filed.call_count` is 0. The test passes alone and failed the push gate on devserver1 at 268badc94 (1 failed, 10602 passed), refusing the push.

## Steps to Reproduce

1. Run the push gate's full suite on 268badc94 (`bash tools/remote-gate.sh push --commit 268badc94b4268c2a3c161ef54be3f24d1385e07 --boundary push`): `tools/tests/test_lean_specs_v65.py:396` fails with `AssertionError: 2 != 0` on `filed.call_count`.
2. Run the test alone (`python3 -m pytest -q tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_tsd_names_the_authors_mutants_and_the_red_run_policy`): it passes.

## Proposed Fix

Patch the name gate resolves at call time (`mock.patch("file_finding.file_finding", ...)`, or patch `sys.modules['file_finding']`), and add a test that replaces `sys.modules['file_finding']` with a fresh copy before the call, so the patch is shown to hold whichever copy is loaded. Check the module for any other patch of an object a lazily imported module is read through.

## Acceptance Criteria

- [ ] **AC1** The red-run policy test holds when another test has replaced `sys.modules['file_finding']` before it runs: `gate.red_run` files through the patched filer and `filed.call_count` is 2
  - **Verify:** shell python3 -m pytest -q tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_red_run_policy_holds_when_file_finding_was_reimported tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_tsd_names_the_authors_mutants_and_the_red_run_policy
  - **Verified:** yes (2026-11-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
| 2026-11-26 | orchestrator | Affects names `changelog.d/BG1762.md`: the builder's fragment records the fix for the release notes; it is the unit's paperwork, so Affects names it |
