# BG1081: remote-gate doctor sources gate-env.sh from its temporary directory, where the gate sources it from the host's home

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/remote-gate.sh, tools/tests/test_remote_gate_doctor.py, tools/tests/test_remote_gate_doctor_env.py, changelog.d/BG1081.md
> **Evidence:** US1077 QA review, round 1 (APPROVE), qa-seat-US1077-r1, 2026-10-19, at e849ccc4: finding 2, tools/remote-gate.sh:272, :295, :311 against :163; a probe printed cwd=host-home for the gate.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T16:32:21Z

## Summary

The doctor extracts its checker into a mktemp directory, cds there, then sources ~/sdlc-gate/gate-env.sh. `cmd_remote` sources the same file from $HOME. A gate-env.sh with a path relative to $HOME, or one that changes directory, gives the doctor a different PATH from the gate's (node, npm and every distribution reported missing) or breaks its checker import (`ModuleNotFoundError: gate_prereqs`), while the same host judges a push green.

## Steps to Reproduce

Write ~/sdlc-gate/gate-env.sh as `export PATH=sdlc-gate/venv/bin:$PATH` (relative to $HOME), or with a `cd` in it, then run `remote-gate.sh doctor`.

## Proposed Fix

Source gate-env.sh from $HOME, as `cmd_remote` does, and import the checker by absolute path.

## Acceptance Criteria

- [ ] **AC1** Given a gate-env.sh that is relative to the host's home or changes directory, when the doctor runs, then it reaches the same verdict as a push judged there
  - **Verify:** pytest tools/tests/test_remote_gate_doctor_env.py::DoctorEnvTests::test_gate_env_is_read_from_the_hosts_home

## Impact

The doctor and the gate can disagree about one host.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
