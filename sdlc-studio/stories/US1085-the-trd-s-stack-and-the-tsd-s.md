# US1085: The TRD's stack and the TSD's framework rows name every dependency the clone installs, and the TSD names each CI job and its trigger

> **Status:** Done
> **Delivers:** CR0644
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_lean_gate_toolchain_docs.py, changelog.d/US1085.md
> **Epic:** EP0290
> **Points:** 2
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer setting up a clone or reading why a gate needs a package
**I want** the TRD's stack and the TSD's framework rows to name every dependency the clone installs, and the TSD to name each CI job and its trigger
**So that** a missing prerequisite or an unexpected CI job is explained by the documents rather than discovered at a red push

## Acceptance Criteria

- **AC1:** Given the packages `requirements-dev.txt` declares and the devDependencies `package.json` declares, when the TRD's technology stack and the TSD's framework rows are read, then each package is named, and the TRD names `requirements-dev.txt` as the one Python dependency list
  - **Verify:** pytest tools/tests/test_lean_gate_toolchain_docs.py::GateToolchainDocsTests::test_every_declared_dependency_is_named
  - **Verified:** yes (2026-10-19)
- **AC2:** Given every job in `.github/workflows/*.yml`, when the TSD is read, then each job is named with the trigger it runs on (push, pull request, schedule, dispatch or tag), read from the workflow files, and the scheduled jobs' baseline file `tools/verify-corpus-baseline.txt` is named with what it compares
  - **Verify:** pytest tools/tests/test_lean_gate_toolchain_docs.py::GateToolchainDocsTests::test_every_ci_job_is_named_with_its_trigger
  - **Verified:** yes (2026-10-19)
- **AC3:** Given the checks `npm run lint` chains in `package.json`, when the TSD is read, then each is named and neither document states how many there are
  - **Verify:** pytest tools/tests/test_lean_gate_toolchain_docs.py::GateToolchainDocsTests::test_every_lint_check_is_named_uncounted
  - **Verified:** yes (2026-10-19)
- **AC4:** Given the oldest Python version the `ci` job installs, when the TRD is read, then the floor it states is that version
  - **Verify:** pytest tools/tests/test_lean_gate_toolchain_docs.py::GateToolchainDocsTests::test_the_python_floor_matches_ci
  - **Verified:** yes (2026-10-19)

## Notes

- Serves: Rowan Achterberg, End goal 3 (D0380 repoint; the card is sdlc-studio/personas/rowan-achterberg-skill-maintainer.md).
- AC1 must fail on: a package added to requirements-dev.txt or package.json devDependencies and named in neither document, or the TRD restoring 'unittest, stdlib, no third-party runner'.
- AC2 must fail on: a scheduled job (corpus, corpus-verify) left out of the TSD, or a job named with the wrong trigger.
- AC3 must fail on: a lint check added to the chain and not named, or 'eight checkers' (or any count) restored.
- AC4 must fail on: the CI floor moving to 3.11 while the TRD still says 3.10.
- Every derived set asserts a known member first (LL0043): `pytest-xdist` among the dependencies, `corpus-verify` among the jobs, `lint:dead-flags` among the lint checks.
- AC4 reads the `ci` job by name: both `ci` and `corpus-verify` install 3.10 and 3.12, so 'the floor job' must be named, not inferred.
- Read the workflow YAML with the same stdlib-only approach the repo's guards use, so the test runs on a clone without PyYAML.
- Covers RV0028 TRD-4, TRD-21, TRD-22, TSD-4, TSD-6, TSD-7, TSD-8, TSD-19. Persona to be repointed to the skill-maintainer card once US1079 lands.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | Claude Opus 5.5 | Groomed: criteria, Verify lines and the mutants each must fail on (D0377) |
| 2026-10-19 | Claude Opus 5.5 | Regroomed after the goal review (round 4): the seats' findings folded in: the corpus baseline named, the ci job named for the floor, known-member floors |
| 2026-10-19 | Claude Opus 5.5 | Repointed at Rowan Achterberg, Primary for the repository-tooling interface, before review (D0379, D0380) |
