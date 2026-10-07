# BG0976: The pre-push hook prints its ssh keepalive warning on every push, even when the clone already carries a keepalive

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .githooks/pre-push, tools/tests/test_pre_push_hook.py, tools/tests/test_pre_push_keepalive.py
> **Evidence:** Found 2026-10-06/07 during the triage session that filed BG0955-BG0963 in this repository.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:37:42Z

## Summary

`.githooks/pre-push` echoes 'the connection must stay up across the gate; set it once with: bash tools/enable-hooks.sh (ssh ServerAliveInterval)' unconditionally (.githooks/pre-push:64). It printed on every push from a clone where `enable-hooks.sh` had just set `core.sshCommand` with `ServerAliveInterval=60`. Advice that prints whether or not it applies is advice people learn to skip, including on the clone where it is needed.

## Steps to Reproduce

`bash tools/enable-hooks.sh` (sets core.sshCommand with a keepalive); `git push` -> the warning still prints.

## Proposed Fix

Print the line only when no keepalive is in force: no `core.sshCommand` carrying ServerAliveInterval at any scope and none in the resolved `ssh -G <host>` configuration.

## Acceptance Criteria

- [ ] **AC1** With a keepalive configured, a push prints no keepalive warning
  - **Verify:** pytest tools/tests/test_pre_push_keepalive.py -k keepalive_warning_silent_when_configured
- [ ] **AC2** With none configured, the warning still prints
  - **Verify:** pytest tools/tests/test_pre_push_keepalive.py -k keepalive_warning_when_absent

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
