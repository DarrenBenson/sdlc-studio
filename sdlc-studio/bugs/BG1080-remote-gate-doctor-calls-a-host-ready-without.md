# BG1080: remote-gate doctor calls a host ready without checking flock and setsid, which every push run on it needs

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/remote-gate.sh, tools/tests/test_remote_gate_doctor.py, tools/tests/test_remote_gate_doctor_runtime.py, changelog.d/BG1080.md
> **Evidence:** US1077 QA review, round 1 (APPROVE), qa-seat-US1077-r1, 2026-10-19, at e849ccc4: finding 1 [LC-018], tools/remote-gate.sh:279 and :325 against :199, :201, :243.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T16:32:17Z

## Summary

host-doctor checks git, Node, npm, python3 and the listed distributions, then prints that the host has what a push needs, and the doctor reports it ready to judge a push. `cmd_remote` has needed flock (the host lock) and setsid (the gate's own session) since US1076. A host without them is called ready, and its first push then fails with exit 4 and `flock: command not found`.

## Steps to Reproduce

A fixture host with every listed distribution plus git, node and npm, but no flock or setsid: `remote-gate.sh doctor` exits 0 'ready'; a push judged there exits 4, 'could not take the gate lock'.

## Proposed Fix

Check every executable `cmd_remote` calls on the host (flock, setsid, and the rest of its runtime) in host-doctor, naming each missing one with its package.

## Acceptance Criteria

- [ ] **AC1** Given a fixture host lacking flock or setsid, when the doctor runs, then it exits non-zero naming the missing command
  - **Verify:** pytest tools/tests/test_remote_gate_doctor_runtime.py::DoctorRuntimeTests::test_a_host_without_flock_or_setsid_is_not_ready

## Impact

The one command that says a host is ready can say so of a host that cannot judge a push.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
