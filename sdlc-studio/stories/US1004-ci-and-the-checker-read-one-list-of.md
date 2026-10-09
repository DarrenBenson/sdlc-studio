# US1004: CI and the checker read one list of suite prerequisites

> **Status:** Draft
> **Delivers:** CR0613
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, tools/tests/test_prereq_list_is_ci_list.py, changelog.d/US1004.md
> **Epic:** EP0278
> **Points:** 2
> **Depends on:** US1003
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose local gate and CI must agree on what the suite needs
**I want** CI's suite install step to install from the same requirements-dev.txt the prerequisite check reads, and the one job that installs differently to stay a declared subset of it
**So that** a package CI starts relying on is a package my clone's checker names, instead of a red push nobody predicted

## Acceptance Criteria

- **AC1:** Given .github/workflows/lint.yml, when the ci job's step that installs the suite's Python packages is read, then it installs from requirements-dev.txt and carries no package list of its own.
  - **Verify:** pytest tools/tests/test_prereq_list_is_ci_list.py::OneListTests::test_the_ci_suite_step_installs_from_requirements_dev
- **AC2:** Given lint.yml's scheduled corpus-verify job, which keeps its own install list, when that list is read, then every package it installs is declared in requirements-dev.txt, with a floor no looser than the file's.
  - **Verify:** pytest tools/tests/test_prereq_list_is_ci_list.py::OneListTests::test_the_corpus_verify_job_installs_a_declared_subset

## Notes

- Release: 6.2 (D0355 breakdown G4, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the inline `pip install --quiet pyyaml pytest pytest-xdist 'coverage>=7.10'` left in that step (lint.yml:76 today)
- AC2 must fail on: the corpus-verify job installing a package, or a looser floor, that requirements-dev.txt does not declare, so the two lists drift apart unseen (bandit at lint.yml:103 is a security-lint step, not a suite prerequisite, and is not read)
- Split out of the first story on the panel's requirement, because the CI edit is the riskiest line and should be reviewed on its own.
- The corpus-verify job (lint.yml:175) is decided explicitly. It keeps `pyyaml pytest 'coverage>=7.10'` without xdist, and the subset criterion pins it instead.
- Moving that job onto the file would add pytest-xdist to a lane compared both ways against tools/verify-corpus-baseline.txt. That would need a re-baseline in the same change, and the effect on the `-n 2` variants in test_lean_tmp_hygiene is UNVERIFIED. A comment on that step says why it differs.
- requirements-dev.txt itself is created by the first story, because the checker reads it. This story only points CI at it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G4 after the refine panel's review |
