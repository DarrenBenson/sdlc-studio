# BG1101: test_repo_hygiene writes probe fixtures into the real scripts/tests directory, so a parallel test copying that tree can fail

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py, changelog.d/BG1101.md
> **Evidence:** devserver1 boundary-suite log for 51231a25 (2026-10-20): test_rehearse_release.py::UpgradeRehearsalTests::test_the_v5_upgrade_strips_retired_tags - shutil.Error on .../scripts/tests/_probe_fixture_deferred.py, No such file or directory. test_repo_hygiene.py:171-177 writes and unlinks that file in TESTS_DIR.
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-20T07:40:39Z

## Summary

`test_repo_hygiene.py`'s `_fixture` writes `<name>.py` into the real .claude/skills/sdlc-studio/scripts/tests directory (`TESTS_DIR)` and unlinks it on cleanup. `test_rehearse_release.py`'s UpgradeRehearsalTests copies the whole skill tree with shutil.copytree. Under pytest-xdist the two can overlap: copytree lists `_probe_fixture_deferred.py`, the hygiene test removes it, and the copy fails with FileNotFoundError. The push of 51231a25 was refused on devserver1 that way, by a change touching neither test.

## Steps to Reproduce

Run the full suite in parallel until `test_the_probe_catches_a_DEFERRED_sibling_import_with_no_path_setup` and `test_the_v5_upgrade_strips_retired_tags` overlap: shutil.Error ... `_probe_fixture_deferred.py` ... [Errno 2] No such file or directory.

## Proposed Fix

Write the probe fixtures into a temporary directory put on the import path for the probe, never into the repository's own tree.

## Acceptance Criteria

- [ ] **AC1** `test_repo_hygiene`'s probe fixtures are written outside the repository's tree, so nothing a parallel test copies can change under it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene_isolation.py::RepoHygieneIsolationTests

## Impact

A push can be refused, and a local suite go red, at random, by a race with no defect in the change under test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | Claude Opus 5.5 | Filed |
