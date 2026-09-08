# BG0654: A push whose pre-push gate outlives the SSH connection git opened before the hook dies with exit 141 after the gate reports PASS, and nothing names the cause

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** tools/enable-hooks.sh, .githooks/pre-push, tools/tests/test_pre_push_hook.py, AGENTS.md
> **Evidence:** 2026-09-07 22:23-22:31Z, `git push origin main` of 28 commits from this clone: the pre-push gate printed `gate: PASS` after 471 s (module-alone 391 s) and the hook exited 0, git exited 141 (SIGPIPE) with no message, origin/main unchanged. The retry with `GIT_SSH_COMMAND='ssh -o ServerAliveInterval=20 -o ServerAliveCountMax=60'` ran the same gate green and landed. Transcript in the session scratchpad, push-out-attempt1.txt.
> **Created:** 2026-09-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

git opens the transport to the remote BEFORE it runs `pre-push`, and only writes the pack after the hook returns. D0180 made the hook pay the full boundary gate, now 471 s on this machine and growing with module-alone, so the SSH session to GitHub sits idle for the whole gate. On the first push of RUN-01M1YK70's plan the server closed that idle session; git's pack write hit a closed socket, git died with 141 and printed nothing, and the operator's view was a green gate followed by a push that did not happen. The hook cannot reach the connection git already holds, but the clone's SSH command can keep it alive, and `tools/enable-hooks.sh` is the one command every clone runs to install the hooks that create the hazard.

## Steps to Reproduce

1. On a clone whose `core.sshCommand` is unset and whose boundary gate takes longer than the remote's idle timeout (about eight minutes here), run `git push origin main`.
2. Read the hook: `gate: PASS`, hook exit 0.
3. Read `echo $?` from git: 141, no message; `git rev-list --count origin/main..HEAD` unchanged.
4. Repeat with `GIT_SSH_COMMAND='ssh -o ServerAliveInterval=20 -o ServerAliveCountMax=60'`: the same gate runs and the push lands.

## Proposed Fix

`tools/enable-hooks.sh` sets `core.sshCommand` for the clone to an ssh with `ServerAliveInterval` and `ServerAliveCountMax` when the clone has none, and says so; the pre-push hook's opening line names the expected duration beside the keepalive the connection needs, so a 141 after a green gate has a named cause; AGENTS.md's push paragraph records the hazard.

## Acceptance Criteria

- [ ] **AC1** Given a clone with no `core.sshCommand`, when `bash tools/enable-hooks.sh` runs, then the clone's `core.sshCommand` names an ssh with `ServerAliveInterval` and `ServerAliveCountMax` set and the script prints the setting; a clone that already sets `core.sshCommand` is left untouched and told so - the paired control.
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::KeepaliveTests::test_enable_hooks_sets_the_keepalive_ssh_command_and_leaves_an_existing_one
- [ ] **AC2** Given the shipped `.githooks/pre-push` driven by subprocess in the existing hook fixture, when it prints its opening estimate, then the line names the keepalive the connection needs across the gate and the command that sets it, on stderr, where the pusher reads it.
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::KeepaliveTests::test_the_hook_names_the_keepalive_the_gate_needs

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in tools/enable-hooks.sh, delete the `core.sshCommand` write so a fresh clone gets no keepalive | Given a clone with no `core.sshCommand`, when `bash tools/enable-hooks.sh` runs, then the clone's `core.sshCommand` names an ssh with `ServerAliveInterval` and `ServerAliveCountMax` set and the script prints the setting; a clone that already sets `core.sshCommand` is left untouched and told so - the paired control. |
| AC2 | in tools/enable-hooks.sh, omit the keepalive from the line that announces what it configured | Given the shipped `.githooks/pre-push` driven by subprocess in the existing hook fixture, when it prints its opening estimate, then the line names the keepalive the connection needs across the gate and the command that sets it, on stderr, where the pusher reads it. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Filed |
