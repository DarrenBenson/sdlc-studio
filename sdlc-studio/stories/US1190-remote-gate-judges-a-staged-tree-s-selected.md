# US1190: remote-gate judges a staged tree's selected test modules on the gate host and returns their verdict

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0663
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/remote-gate.sh, tools/tests/test_remote_gate_selected.py
> **Epic:** EP0325
> **Points:** 5
> **Persona:** Rowan Achterberg

## User Story

**As a** Rowan Achterberg
**I want** remote-gate judges a staged tree's selected test modules on the gate host and returns their verdict
**So that** CR0663 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The host judges exactly the staged tree and runs only the selected modules

- **Given** a clone with `sdlc.gateHost` set (the fixture's local transport standing in for ssh), a change staged and not committed, an unstaged edit and an untracked file beside it
- **When** `tools/remote-gate.sh` is run in its staged-tree mode with a list of selected test modules (the usage line names the flags)
- **Then** the tree checked out on the host holds the staged content and neither the unstaged edit nor the untracked file, only the named modules run there, and the exit is 0 when they pass; the clone's HEAD, index, working tree and refs are as they were. Fails on: the host judging HEAD or the working tree, the whole suite running, or the clone gaining a commit or a ref
- **Verify:** pytest tools/tests/test_remote_gate_selected.py::RemoteGateSelectedTests::test_the_host_judges_the_staged_tree_and_only_the_selected_modules

### AC2: A red module refuses with its output relayed

- **Given** a staged change that makes one selected module fail
- **When** the staged-tree mode runs
- **Then** it exits 1 and the failing test's name and output reach the caller's stderr. Fails on: a red run reported as green, or as a connection failure the caller would retry locally
- **Verify:** pytest tools/tests/test_remote_gate_selected.py::RemoteGateSelectedTests::test_a_red_selected_module_exits_1_with_its_output

### AC3: A host that cannot be reached or cannot start is not a test verdict

- **Given** a transport that fails to connect, then a host whose setup refuses before any test runs, then a call naming no module
- **When** the staged-tree mode runs on each
- **Then** the exits are 3, 4 and 2 in that order, each with a line naming the cause, and none is 0 or 1. Fails on: an unreachable host read as a red suite, or as a green one
- **Verify:** pytest tools/tests/test_remote_gate_selected.py::RemoteGateSelectedTests::test_an_unreachable_or_unready_host_is_not_a_verdict

### AC4: The host's run directory is removed and runs there stay serialised

- **Given** two staged-tree runs started against one host, and a third whose caller goes away mid-run
- **When** they finish or are interrupted
- **Then** the two verdicts are each the right one for their own tree, taken under the host's lock one after the other, and no run's tree is left on the host afterwards. Fails on: two selections sharing a checkout, or an interrupted commit leaking its tree on the host
- **Verify:** pytest tools/tests/test_remote_gate_selected.py::RemoteGateSelectedTests::test_runs_are_serialised_and_leave_no_tree_on_the_host

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
