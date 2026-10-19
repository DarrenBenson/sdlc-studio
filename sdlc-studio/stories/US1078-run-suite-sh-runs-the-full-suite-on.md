# US1078: run-suite.sh runs the full suite on the gate host and records a verdict its check can read

> **Status:** Draft
> **Delivers:** CR0635
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/run-suite.sh, tools/remote-gate.sh, tools/tests/test_run_suite_remote.py, AGENTS.md, changelog.d/US1078.md
> **Epic:** EP0288
> **Points:** 3
> **Depends on:** US1075
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer about to commit a change to shared surface
**I want** `tools/run-suite.sh` to run the full suite on the configured gate host over the same tree it already binds its verdict to
**So that** I can keep the full-suite-before-commit rule when my workstation cannot hold the suite, and the verdict is one `run-suite.sh --check` reads

## Acceptance Criteria

- **AC1:** Given a configured host and a working tree whose change breaks a test, when `tools/run-suite.sh all` runs, then the tree run-suite already hashes is wrapped as a commit, sent and run on the host, and the wrapper exits non-zero naming the failing test
  - **Verify:** pytest tools/tests/test_run_suite_remote.py::RunSuiteRemoteTests::test_the_hashed_tree_is_what_runs
- **AC2:** Given a staged green change beside an unstaged edit that breaks a test, when the wrapper runs on the host, then the run is red
  - **Verify:** pytest tools/tests/test_run_suite_remote.py::RunSuiteRemoteTests::test_an_unstaged_red_edit_is_judged
- **AC3:** Given a green host run, when `run-suite.sh --check` runs, then it exits 0, and after one further edit it refuses
  - **Verify:** pytest tools/tests/test_run_suite_remote.py::RunSuiteRemoteTests::test_check_reads_the_host_verdict
- **AC4:** Given the same tree, when the wrapper runs with no host configured, then the suite runs locally, and with one configured it runs on the host
  - **Verify:** pytest tools/tests/test_run_suite_remote.py::RunSuiteRemoteTests::test_the_suite_runs_where_the_configuration_says

## Notes

- Serves: Rowan Achterberg, End goal 4 (D0380 repoint; the card is sdlc-studio/personas/rowan-achterberg-skill-maintainer.md).
- Release: 6.2 (second run, D0365) (refine breakdown G14, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the wrapper sends HEAD instead of the hashed tree
- AC2 must fail on: the wrapper sends only the index, recording a green over an unstaged red edit
- AC3 must fail on: the host's verdict is not written to the local suite verdict
- AC4 must fail on: the wrapper ignores `sdlc.gateHost`
- Wrap `tree_state()`'s tree with `git commit-tree` on a scratch ref; nothing is added to the branch (run-suite.sh:63-108, BG0492).

## Grooming note (2026-10-19)

- The shipped `reference-sprint-toolchain.md` is dropped from Affects: its two run-suite rows (run a suite, confirm its verdict) mean the same wherever the suite runs, so the unit stays wholly repository tooling and is judged against the skill maintainer (D0379, D0380). `tools/remote-gate.sh` joins Affects: the wrapper reuses US1075's send rather than duplicating it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-12 | Claude Opus 5.5 (engineering seat) | Groomed from the refine breakdown G14 after the refine panel's review |
| 2026-10-19 | Claude Opus 5.5 | Regroomed after the goal review (round 4): the seats' findings folded in: the shipped runbook dropped from Affects, remote-gate.sh added |
| 2026-10-19 | Claude Opus 5.5 | Repointed at Rowan Achterberg, Primary for the repository-tooling interface, before review (D0379, D0380) |
