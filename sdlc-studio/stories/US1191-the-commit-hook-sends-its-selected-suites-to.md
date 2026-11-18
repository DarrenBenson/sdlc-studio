# US1191: The commit hook sends its selected suites to the named gate host, and runs them locally when the host cannot be reached

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0663
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/commit-msg, CONTRIBUTING.md, tools/tests/test_commit_suites_remote.py
> **Epic:** EP0325
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The commit hook sends its selected suites to the named gate host, and runs them locally when the host cannot be reached
**So that** CR0663 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: With a gate host named the selected suites run there and not here

- **Given** a fixture clone with `sdlc.gateHost` set, a staged change whose pre-commit pass selected test modules, and stubs recording what `tools/remote-gate.sh` and the local runners are called with
- **When** `.githooks/commit-msg` runs
- **Then** the selection is sent to the host through remote-gate's staged-tree mode, no local suite runner starts, the hook passes on the host's 0 and refuses on its 1 with the host's output shown. Fails on: the suites run in both places, or still run locally with a host named
- **Verify:** pytest tools/tests/test_commit_suites_remote.py::CommitSuitesRemoteTests::test_a_named_host_runs_the_selected_suites_and_the_laptop_runs_none

### AC2: An unreachable or unready host falls back to a local run, and says so

- **Given** the same clone with the remote call exiting 3, then 4
- **When** the hook runs
- **Then** each time it prints one line naming the host and the cause, runs the same selection locally, and its verdict is that local run's. Fails on: a commit refused only because the host was down, or accepted with no suite having run anywhere
- **Verify:** pytest tools/tests/test_commit_suites_remote.py::CommitSuitesRemoteTests::test_an_unreachable_host_falls_back_to_the_local_suites

### AC3: With no host, or with SDLC_GATE_LOCAL=1, nothing connects

- **Given** a clone with no `sdlc.gateHost`, and one with a host named and `SDLC_GATE_LOCAL=1` in the environment
- **When** the hook runs with suites selected
- **Then** the suites run locally as they do today and remote-gate is never called. Fails on: a connection attempted from a clone that names no host, or the documented local override ignored at commit time
- **Verify:** pytest tools/tests/test_commit_suites_remote.py::CommitSuitesRemoteTests::test_no_host_or_the_local_override_runs_the_suites_here

### AC4: CONTRIBUTING says where a commit's suites run

- **Given** CONTRIBUTING.md's section on hooks and the push
- **When** a contributor reads how a commit is judged
- **Then** it says the commit hook sends its selected suites to `sdlc.gateHost` when one is named, falls back to a local run when the host cannot be reached, and that `SDLC_GATE_LOCAL=1` keeps them local. Fails on: a page saying only the push uses the gate host
- **Verify:** pytest tools/tests/test_commit_suites_remote.py::CommitSuitesRemoteTests::test_contributing_says_where_the_commit_suites_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
