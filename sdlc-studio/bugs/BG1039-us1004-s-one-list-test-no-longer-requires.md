# BG1039: US1004's one-list test no longer requires `-r` on the suite step, and still checks hand installs against its own list of four packages

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_prereq_list_is_ci_list.py, changelog.d/BG1039.md
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T13:54:46Z

## Summary

From US1004's round-2 QA review on 2026-10-13 (APPROVE, nothing blocking). (1) The repair dropped round 1's `assertIn("-r requirements-dev.txt", command)`, so AC1's own test passes when the suite step reads `python -m pip install --quiet -c requirements-dev.txt`, which installs nothing; the sibling pins (xdist before the suite, coverage before the suite, the corpus job's coverage) still fail on it, so the suite catches it. (2) `SUITE_PACKAGES` in `test_prereq_list_is_ci_list.py` is a hand-kept second list: with a fifth package added to requirements-dev.txt and a separate ci step hand-installing it, every pin passes, and a later hand install with a different floor could override the file's floor in CI while the checker reads the file.

## Steps to Reproduce

Change the ci suite step to `-c requirements-dev.txt`: the AC1 test passes. Add pytest-timeout to requirements-dev.txt and a ci step `pip install pytest-timeout`: every pin passes.

## Proposed Fix

Require `-r requirements-dev.txt` on the suite step again, and judge hand installs against `_declared()` (the file) rather than a second list.

## Acceptance Criteria

- [ ] **AC1** Given the ci suite step reading `-c requirements-dev.txt`, when the one-list test runs, then it fails
  - **Verify:** pytest tools/tests/test_prereq_list_is_ci_list_strict.py::StrictOneListTests::test_the_suite_step_installs_with_r
- [ ] **AC2** Given a package declared in requirements-dev.txt and installed by hand in another ci step, when the one-list test runs, then it fails
  - **Verify:** pytest tools/tests/test_prereq_list_is_ci_list_strict.py::StrictOneListTests::test_no_declared_package_is_installed_by_hand

## Impact

Low: the suite still catches the first shape through sibling pins; the second lets a CI-only floor drift from what the checker reads.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): already fixed: both mutants it names are now refused, fixed by 6456f66f (BG1053) and 95e5e3f8 (BG1056) |
