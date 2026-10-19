# BG1085: remote-gate doctor prints the local clone's Python install route for a gap on the gate host

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/remote-gate.sh, tools/gate_prereqs.py, tools/tests/test_remote_gate_doctor.py, tools/tests/test_remote_gate_doctor_route.py, changelog.d/BG1085.md, tools/tests/test_gate_prereqs.py
> **Evidence:** US1077 QA review, round 1 (APPROVE), qa-seat-US1077-r1, 2026-10-19, at e849ccc4: finding 6, tools/gate_prereqs.py:120-133, tools/remote-gate.sh:272.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T16:32:37Z

## Summary

host-doctor reuses `gate_prereqs.install_route()`, written for a clone. On the host it names `-r requirements-dev.txt`, a file the host does not keep (the doctor deletes its temporary directory), and its venv route ends with `export PATH=...`, which the gate never reads: the gate reads ~/sdlc-gate/gate-env.sh. The route suits the interpreter but cannot be run as written on the host.

## Steps to Reproduce

Run the doctor against a host lacking pytest-xdist and read the Install: route.

## Proposed Fix

Give the host its own route: install the named distributions by name, and put a venv on PATH through ~/sdlc-gate/gate-env.sh.

## Acceptance Criteria

- [ ] **AC1** Given a host lacking a distribution, when the doctor runs, then its install route names the distribution itself and ~/sdlc-gate/gate-env.sh, never requirements-dev.txt or a shell export
  - **Verify:** pytest tools/tests/test_remote_gate_doctor_route.py::DoctorRouteTests::test_the_host_gets_a_host_route

## Impact

A person following the doctor's advice on the host is left with a command that fails or does nothing for the gate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
