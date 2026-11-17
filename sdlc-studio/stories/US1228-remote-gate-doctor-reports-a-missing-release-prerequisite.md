# US1228: Remote gate doctor reports a missing release prerequisite under the gate's own environment and names the fix

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0687
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/remote-gate.sh, tools/tests/test_remote_gate_doctor.py
> **Epic:** EP0336
> **Points:** 2
> **Persona:** Rowan Achterberg

## User Story

**As a** Rowan Achterberg
**I want** Remote gate doctor reports a missing release prerequisite under the gate's own environment and names the fix
**So that** CR0687 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A missing release prerequisite is reported with its fix

- **Given** a gate host that has everything a push needs but no Python 3.10 on the PATH its `gate-env.sh` sets
- **When** `bash tools/remote-gate.sh doctor` is run against it
- **Then** the output names Python 3.10 as a release gate prerequisite the host lacks and names the fix (put the tool on the PATH `gate-env.sh` sets, last, so the venv's `python3` still wins), while the push verdict is unchanged: the host reads ready to judge a push and the exit is 0. Fails on: a doctor that says nothing of the release gate, or one whose push verdict turns red on a release-only gap
- **Verify:** pytest tools/tests/test_remote_gate_doctor.py::GateHostDoctorTests::test_a_missing_release_prerequisite_is_named_with_its_fix

### AC2: The release check runs under the gate's own environment

- **Given** a host where Python 3.10 and pdftotext resolve only on the PATH that `gate-env.sh` adds, not on the PATH an ssh command starts with
- **When** `bash tools/remote-gate.sh doctor` is run against it
- **Then** no release prerequisite is reported missing and the output says the host has what the release gate needs. Fails on: a check made before `gate-env.sh` is sourced, which would report a tool the gate itself can find
- **Verify:** pytest tools/tests/test_remote_gate_doctor.py::GateHostDoctorTests::test_the_release_check_runs_under_the_gate_environment

### AC3: Each missing release tool gets its own line

- **Given** a host that lacks both Python 3.10 and pdftotext under `gate-env.sh`
- **When** `bash tools/remote-gate.sh doctor` is run against it
- **Then** each tool is named on its own line with its fix, in the same words `gate_prereqs.py check --release` uses for the gap. Fails on: only the first gap reported, or a second list of release prerequisites kept in the shell script
- **Verify:** pytest tools/tests/test_remote_gate_doctor.py::GateHostDoctorTests::test_each_missing_release_tool_is_named_from_the_one_list

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
