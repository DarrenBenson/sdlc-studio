# BG1038: The pre-push keepalive check reads GIT_SSH above core.sshCommand, the reverse of git's order, and asks ssh -G without the configured command's own options

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .githooks/pre-push, tools/tests/test_pre_push_keepalive_order.py, changelog.d/BG1038.md
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T13:28:58Z

## Summary

From BG0976's round-2 QA review on 2026-10-13 (APPROVE, nothing blocking). (1) git uses `GIT_SSH_COMMAND`, then core.sshCommand, then `GIT_SSH`; the hook's keepalive check blanks the command whenever `GIT_SSH` is set, so with `GIT_SSH`=/usr/bin/ssh beside the keepalive core.sshCommand enable-hooks.sh writes, the advice prints though the ssh git runs carries ServerAliveInterval=60. The output equals the base ref's, but the changelog's 'or else core.sshCommand at any scope', the hook comment and the commit message are false in that case, and deleting the branch passes every test. (2) The ssh -G read runs a bare `ssh -G -- <host>`, but a configured command's own options override `ssh_config`: core.sshCommand `ssh -o ServerAliveInterval=0`, or `GIT_SSH_COMMAND` `ssh -F /dev/null`, over an `ssh_config` keepalive reads silent though the ssh git runs has none. Needs an explicit opt-out over a config keepalive; the bug's Proposed Fix prescribed the ssh -G approximation.

## Steps to Reproduce

Set core.sshCommand to the enable-hooks.sh keepalive and `GIT_SSH`=/usr/bin/ssh, push to a local remote: the advice prints. Set core.sshCommand `ssh -o ServerAliveInterval=0` with an `ssh_config` that sets a keepalive for an scp remote's host: the advice is silent.

## Proposed Fix

Read `GIT_SSH_COMMAND`, then core.sshCommand, and only then `GIT_SSH`; run `ssh -G` with the configured command's own options (as git runs the command to detect the ssh variant), so an explicit opt-out wins over `ssh_config.`

## Acceptance Criteria

- [ ] **AC1** Given `GIT_SSH` set beside a keepalive core.sshCommand, when the hook runs, then it is silent, as git runs core.sshCommand
  - **Verify:** pytest tools/tests/test_pre_push_keepalive_order.py::KeepaliveOrderTests::test_core_ssh_command_wins_over_git_ssh
- [ ] **AC2** Given a configured ssh command that sets ServerAliveInterval=0 over an `ssh_config` keepalive, when the hook runs for that host, then it prints the advice
  - **Verify:** pytest tools/tests/test_pre_push_keepalive_order.py::KeepaliveOrderTests::test_an_explicit_opt_out_wins_over_ssh_config

## Impact

Low: in two uncommon configurations the advice is printed when not needed, or withheld when needed; a release note and a comment say more than the code does.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
