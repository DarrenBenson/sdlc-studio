# BG1084: remote-gate doctor's exit codes are documented as 0, 1 and 3, and a missing transport is reported as an unready host

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/remote-gate.sh, changelog.d/US1077.md, tools/tests/test_remote_gate_doctor.py, tools/tests/test_remote_gate_doctor_exits.py, changelog.d/BG1084.md
> **Evidence:** US1077 QA review, round 1 (APPROVE), qa-seat-US1077-r1, 2026-10-19, at e849ccc4: finding 5, changelog.d/US1077.md:10-11, tools/remote-gate.sh:16 and :273-283.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T16:32:33Z

## Summary

The changelog and the script header list 0 ready, 1 not, 3 unreachable. The doctor also exits 2 when no host is configured or HEAD lacks its files. An sdlc.gateSsh naming a command that does not exist (rc 127) is reported as '<host> is NOT ready' with exit 1, a transport fault read as a host fault.

## Steps to Reproduce

`git config sdlc.gateSsh /nonexistent && bash tools/remote-gate.sh doctor` -> exit 1, 'NOT ready'.

## Proposed Fix

Document exit 2, and report a transport that cannot start (126, 127) as a transport failure.

## Acceptance Criteria

- [ ] **AC1** Given an sdlc.gateSsh that cannot start, when the doctor runs, then it exits 3 as a transport failure, and the documented exits include 2
  - **Verify:** pytest tools/tests/test_remote_gate_doctor_exits.py::DoctorExitTests::test_a_transport_that_cannot_start_is_exit_3

## Impact

A caller reading the exit code, or a person reading the verdict, is sent to fix the wrong machine.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
