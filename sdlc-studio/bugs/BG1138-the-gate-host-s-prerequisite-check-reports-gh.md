# BG1138: The gate host's prerequisite check reports gh missing with a consequence that is false there, so every push says the red-CI read is off when it ran

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/gate_prereqs.py, tools/remote-gate.sh, tools/tests/test_gate_prereqs.py, changelog.d/BG1138.md
> **Evidence:** Push of a0fff9cc on 2026-10-31: the note appears among the host gate's lines; `gh run list --workflow Lint --branch main --event push` locally returns run 41236425306, success, headSha a0fff9cc; `ssh devserver1 command -v gh` finds nothing; the hook prints no `CI state UNREAD` line.
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-31T21:19:46Z

## Summary

With sdlc.gateHost set, tools/remote-gate.sh runs `gate_prereqs.py check --refusing` on the host, and the host has no gh, so every push prints `note: gh is not found - the red-CI read before a push reads UNREAD`. The red-CI read runs in the local pre-push hook, not on the host. On 2026-10-31 the local read found Lint run 41236425306 green and printed nothing, but the note led the agent to tell the operator that the CI check had not run and that gh needed installing.

## Steps to Reproduce

1. Set sdlc.gateHost to a host that has no gh (devserver1 today).
2. Push from a clone whose local gh is installed and logged in.
3. Expected: no gh note, since gh is not needed on the host. Actual: the host's preflight prints the note naming the red-CI read as UNREAD, while the local hook read CI successfully and printed no UNREAD line.

## Proposed Fix

Give `gate_prereqs.py` a host mode (or a per-tool scope) so that the host-side preflight in remote-gate.sh leaves out a tool used only by the local hook. The local check, and enable-hooks.sh, still name a missing gh.

## Acceptance Criteria

- [ ] **AC1** The host-side preflight that remote-gate.sh runs does not name gh as a missing prerequisite.
  - **Verify:** pytest tools/tests/test_gate_prereqs.py
- [ ] **AC2** The local check (`gate_prereqs.py check` with no host flag) still names a missing gh with its consequence, and still exits 0 for it under --refusing.
  - **Verify:** pytest tools/tests/test_gate_prereqs.py

## Impact

A false diagnostic on every gated push about a safety guard: it can send the operator to install gh on the host for nothing, or make them believe the red-main check is off.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | claude | Filed |
