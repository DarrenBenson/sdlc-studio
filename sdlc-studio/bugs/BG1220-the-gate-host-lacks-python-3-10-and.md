# BG1220: The gate host lacks Python 3.10 and pdftotext, so the release route reads three passing criteria red

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/gate_prereqs.py, tools/remote-gate.sh, tools/tests/test_gate_prereqs.py, changelog.d/BG1220.md
> **Evidence:** scratchpad run5/release-gate.log, 2026-11-04; BG1181.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T19:56:50Z

## Summary

2026-11-04, run five's done-check: `remote-gate.sh push --commit 8f44ea1c --release` on devserver1. US0908 AC1 and AC2 (tools/tests/`test_lean_python_floor.py`, every tracked file compiles and every shipped script starts under Python 3.10) and US0957 AC3 (`pdftotext docs/whitepaper.pdf - | grep -q 'v6'`) read red there and pass on this machine. devserver1 has no Python 3.10 (`uv python find 3.10` finds none) and no pdftotext. BG1181 records that `gate_prereqs` ignores Python 3.10; nothing names pdftotext. The host's push-boundary prerequisite check reported every prerequisite present, because the release lane's needs are not in its list.

## Steps to Reproduce

1. `ssh devserver1 'uv python find 3.10; which pdftotext'`.
2. `remote-gate.sh push --commit <sha> --release`: the three criteria read red.

## Proposed Fix

Name Python 3.10 and pdftotext as release-route prerequisites in `gate_prereqs`, check them before the host's release gate starts, and install both on the gate host (uv python install 3.10, and poppler's pdftotext).

## Acceptance Criteria

- [ ] **AC1** The release route refuses before the gate starts, naming each missing release prerequisite, on a host without Python 3.10 or pdftotext.
  - **Verify:** pytest tools/tests/test_gate_prereqs.py
  - **Verified:** yes (2026-11-05)

## Impact

Every release gate run through US1114's route reads three passing criteria red, so the route cannot pass first time.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
