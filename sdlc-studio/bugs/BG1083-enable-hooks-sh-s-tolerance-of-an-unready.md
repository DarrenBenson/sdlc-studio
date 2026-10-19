# BG1083: enable-hooks.sh's tolerance of an unready or unreachable gate host has no test

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_remote_gate_doctor.py, tools/tests/test_enable_hooks_gate_host.py, changelog.d/BG1083.md
> **Evidence:** US1077 QA review, round 1 (APPROVE), qa-seat-US1077-r1, 2026-10-19, at e849ccc4: finding 4, tools/enable-hooks.sh:51.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T16:32:29Z

## Summary

tools/enable-hooks.sh runs `bash tools/remote-gate.sh doctor || true`. Without the `|| true`, an unready host (exit 1) or an unreachable one (exit 3) stops the script under `set -e` before its keepalive step, leaving core.sshCommand unset (the behaviour BG0654 added). AC3's test drives only a ready host, so the module stays green.

## Steps to Reproduce

Remove `|| true` from the doctor line in tools/enable-hooks.sh, then run tools/tests/`test_remote_gate_doctor.py`: green.

## Proposed Fix

Drive enable-hooks.sh against an unready and an unreachable host and assert it still sets the keepalive.

## Acceptance Criteria

- [ ] **AC1** Given an unready or unreachable gate host, when enable-hooks.sh runs, then it still completes and sets the keepalive
  - **Verify:** pytest tools/tests/test_enable_hooks_gate_host.py::EnableHooksGateHostTests::test_an_unready_host_does_not_stop_setup

## Impact

A later edit can make setup stop half-way on any clone whose host is down.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
