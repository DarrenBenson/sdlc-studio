# BG1101: test_repo_hygiene writes probe fixtures into the real scripts/tests directory, so a parallel test copying that tree can fail

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py, changelog.d/BG1101.md
> **Evidence:** devserver1 boundary-suite log for 51231a25 (2026-10-20): test_rehearse_release.py::UpgradeRehearsalTests::test_the_v5_upgrade_strips_retired_tags - shutil.Error on .../scripts/tests/_probe_fixture_deferred.py, No such file or directory. test_repo_hygiene.py:171-177 writes and unlinks that file in TESTS_DIR.
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-20T07:40:39Z

## Summary

`test_repo_hygiene.py`'s `ProbeMechanismTests._fixture` writes `<name>.py` into the real .claude/skills/sdlc-studio/scripts/tests directory (`TESTS_DIR`), unlinks it on cleanup, and removes the whole `tests/__pycache__` with `shutil.rmtree`, every other module's bytecode with it. `test_rehearse_release.py`'s UpgradeRehearsalTests copies the whole skill tree with shutil.copytree. Under pytest-xdist the two can overlap: copytree lists `_probe_fixture_deferred.py`, the hygiene test removes it, and the copy fails with FileNotFoundError. The push of 51231a25 was refused on devserver1 that way, by a change touching neither test.

## Steps to Reproduce

1. Copy `.claude/skills/sdlc-studio/scripts` to a scratch directory.
2. Run the copy's `ProbeMechanismTests` with `pathlib.Path.write_text` wrapped to log each path.

Measured at HEAD 3791e5193: the run writes `scripts/tests/_probe_fixture_deferred.py` and
`scripts/tests/_probe_fixture_correct.py` into the tests directory itself, and leaves no
`tests/__pycache__` behind. In the full suite under xdist, any test copying the skill tree
(UpgradeRehearsalTests' `shutil.copytree`) can list a file the cleanup then removes; that is
the refused push of 51231a25.

## Proposed Fix

Build each probe fixture in a temporary `scripts/`-shaped directory with its own `tests/`
package (and a `gitutil.py` beside it for the module that sets its path up), and give `_probe`
the directory to run from, so the probe still imports `tests.<mod>` from a `scripts/` cwd.
Nothing is written into, or removed from, the repository's own tree.

## Acceptance Criteria

- [ ] **AC1** Given the repository's `scripts/tests/` directory, when ProbeMechanismTests runs, then no file is created in it or removed from it and its `__pycache__` is left as it was. Fails on: HEAD's `_fixture`, which writes `_probe_fixture_deferred.py` and `_probe_fixture_correct.py` into it and removes `tests/__pycache__` whole (measured in a copy).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py::ProbeIsolationTests::test_the_probe_fixtures_write_nothing_into_the_repository_tree
  - **Verified:** yes (2026-11-23)
- [ ] **AC2** Given fixtures built outside the tree, when the probe runs, then it still reports the module whose `gitutil` import is deferred with no path set up, naming `gitutil`, and passes the module that sets its path up. Fails on: a fix that moves the fixtures but leaves `_probe` running from the real `scripts/`, where the fixture module is not found and the catch is of the wrong import.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py::ProbeMechanismTests
  - **Verified:** yes (2026-11-23)

## Impact

A push can be refused, and a local suite go red, at random, by a race with no defect in the change under test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-23 | Sam Eriksson (qa) | Groomed for run twenty-four: reproduced at HEAD in a copy (two fixture files written into `tests/` and `tests/__pycache__` removed whole); the Verify on a module that does not exist replaced by two executable criteria in test_repo_hygiene.py, a detection control among them; Affects drops test_repo_hygiene_isolation.py |
