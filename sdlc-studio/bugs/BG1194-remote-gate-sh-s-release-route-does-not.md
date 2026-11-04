# BG1194: remote-gate.sh's release route does not send SDLC_GATE_BOUNDARY, so a value set in the shell changes the local release gate but not the host's

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/remote-gate.sh, tools/tests/test_remote_gate_release.py, sdlc-studio/trd.md, sdlc-studio/tsd.md, changelog.d/BG1194.md
> **Evidence:** US1114 builder report, 2026-11-04, outside-the-unit item 1.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T08:56:03Z

## Summary

2026-11-04, US1114's build (run five). US1114 sends `SDLC_VERIFY_TIMEOUT`, `SDLC_VERIFY_BATCH_TIMEOUT`, `SDLC_VERIFY_WORKERS` and `SDLC_STUDIO_BOUNDARY_SUITE` to the host for `remote-gate.sh push --commit <sha> --release`, but not `SDLC_GATE_BOUNDARY` (gate.py:2706). Its builder first sent it, but `test_lean_gate_host_docs::test_every_gate_host_setting_is_named` requires every `SDLC_GATE_*` name in remote-gate.sh to appear in the TRD's and TSD's push-gate sections, which were outside US1114's Affects. With the variable set in the shell, a local `gate.py --release` and the host's disagree on the boundary.

## Steps to Reproduce

1. `export SDLC_GATE_BOUNDARY=<value>`.
2. Run `remote-gate.sh push --commit <sha> --release` against a stub host and read the environment the host's gate receives: the variable is absent.

## Proposed Fix

Send `SDLC_GATE_BOUNDARY` on the release route with the same refusal-by-name as the other settings, and name it in the TRD's and TSD's push-gate sections.

## Acceptance Criteria

- [ ] **AC1** With `SDLC_GATE_BOUNDARY` set locally, the host's release gate reads the same value, and the TRD and TSD push-gate sections name it.
  - **Verify:** pytest tools/tests/test_remote_gate_release.py tools/tests/test_lean_gate_host_docs.py

## Impact

The release route's promise that the host reads what the local shell has is broken for one setting.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
