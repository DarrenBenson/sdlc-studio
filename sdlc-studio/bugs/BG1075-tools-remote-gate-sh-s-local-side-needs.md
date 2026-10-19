# BG1075: tools/remote-gate.sh's local side needs bash 4, so a pusher on stock macOS bash 3.2 has every gate-host push refused

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/remote-gate.sh, tools/tests/test_remote_gate_push.py, CONTRIBUTING.md, changelog.d/BG1075.md
> **Evidence:** US1075 round-2 QA verdict (sdlc-studio/reviews/critic-verdicts.md), its [new] finding; tools/remote-gate.sh `local -A held=()`; install.sh avoids bash-4 syntax for macOS.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T13:07:49Z

## Summary

The local side of tools/remote-gate.sh uses `local -A` (an associative array, bash 4.0) to prune the host's stale refs, and US1076 adds `exec {fd}< <(...)` (bash 4.1) and `$!` for a process substitution (bash 4.4). macOS ships bash 3.2, which install.sh is written to tolerate; under it the local side aborts before the send, so every host-path push is refused (it fails closed, and `SDLC_GATE_LOCAL`=1 runs the gate locally). Found by US1075's round-2 QA reviewer as a non-blocking [new] finding.

## Steps to Reproduce

Run `bash tools/remote-gate.sh push --commit <sha>` under bash 3.2 with sdlc.gateHost set -> `local: -A: invalid option`, then an unbound-variable abort before anything is sent.

## Proposed Fix

Keep the local side to bash 3.2: membership by a newline-delimited string, a fixed descriptor for the feeder, and the feeder's pid taken another way; or refuse on bash < 4 with a message naming the requirement, and say so in CONTRIBUTING.

## Acceptance Criteria

- [ ] **AC1** The local side of remote-gate.sh runs under bash 3.2, or refuses there with a message naming the bash it needs
  - **Verify:** pytest tools/tests/test_remote_gate_push.py -k runs_where_the_configuration_says

## Impact

A contributor on stock macOS cannot use a gate host without installing a newer bash.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
