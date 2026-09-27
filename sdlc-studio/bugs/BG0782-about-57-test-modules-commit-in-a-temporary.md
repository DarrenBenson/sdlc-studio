# BG0782: About 57 test modules commit in a temporary git repo with auto-maintenance on, the race BG0711 fixed in one

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** conftest.py, tools/skill-tests.sh, .claude/skills/sdlc-studio/scripts/tests/test_lean_git_maintenance_off.py, tools/tests/test_lean_git_maintenance_off.py, changelog.d/BG0782.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T20:32:48Z

## Summary

BG0711 traced a CI flake to git 2.55's detached 'git maintenance run --auto --detach', which outlives the commit and writes into .git while TemporaryDirectory's cleanup removes it (Errno 39). BG0711 fixed `test_complexity.py` only. 38 modules in scripts/tests and 19 in tools/tests run git commit inside a TemporaryDirectory with default cleanup and auto-maintenance on. Found by BG0711's QA review.

## Steps to Reproduce

grep -l 'git.*commit' scripts/tests tools/tests; each runs on CI's git 2.55 with maintenance.auto unset.

## Proposed Fix

Set maintenance.auto=false suite-wide through `GIT_CONFIG_COUNT`/KEY/VALUE in the root conftest and tools/skill-tests.sh, with one test that a fixture repo reads it false.

## Acceptance Criteria

- [ ] **AC1** Given a pytest session over either test tree, when a test makes a fixture repository with `git init` in a temporary directory, then `git config maintenance.auto` reads false there. Fails on: HEAD, where only test_complexity.py turns it off (BG0711) and about 110 modules commit in temporary repositories with detached maintenance on
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_git_maintenance_off.py::GitMaintenanceOffTests::test_a_fixture_repo_reads_maintenance_off
- [ ] **AC2** Given `tools/skill-tests.sh` running that module under unittest, when the environment already carries one `GIT_CONFIG_COUNT` entry, then the module passes and the existing entry is still in force. Fails on: setting the variable only in conftest.py, which unittest never loads, or overwriting `GIT_CONFIG_COUNT` and dropping a setting the caller made
  - **Verify:** pytest tools/tests/test_lean_git_maintenance_off.py::SkillTestsMaintenanceTests::test_skill_tests_turns_maintenance_off_and_keeps_existing_config

## Notes

- Sprint 6 engineering: follows the TMPDIR precedent exactly (conftest.py for pytest, tools/skill-tests.sh for unittest). Local git is 2.53, so the race cannot be reproduced here; CI runs 2.55. Rough count at dee380d9: 77 script test modules and 34 tools test modules both commit and use TemporaryDirectory. In v6.0.0 because `tag-check` needs forge CI green on the exact tagged commit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | Groomed for Sprint 6: criteria and Verify selectors written |
