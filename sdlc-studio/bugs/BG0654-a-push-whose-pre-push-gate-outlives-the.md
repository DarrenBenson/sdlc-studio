# BG0654: A push whose pre-push gate outlives the SSH connection git opened before the hook dies with exit 141 after the gate reports PASS, and nothing names the cause

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
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

- [ ] **AC1** Given a throwaway clone whose LOCAL config carries no `core.sshCommand`, and an environment with `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` POINTED AT `/dev/null` so the developer's own `~/.gitconfig` cannot answer for the clone. Unsetting those two is what LETS it answer, which is the opposite of what this control needs, and pointing them at a null file is the mechanism the module's own git helper already uses, when `bash tools/enable-hooks.sh` runs, then `git config --local core.sshCommand` names an ssh carrying `ServerAliveInterval` and `ServerAliveCountMax`, and the script prints what it set
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::KeepaliveTests::test_enable_hooks_sets_the_keepalive_on_a_clone_that_has_none
  - **Verified:** yes (2026-09-09)
- [ ] **AC2** Given a clone whose LOCAL `core.sshCommand` is already set to something else, when the script runs in the same scrubbed environment, then that value is unchanged and the script says it left it alone. This is the paired control AC1 cannot supply: deleting the write satisfies "an existing one is untouched" trivially, and the likelier careless implementation is an unconditional write that clobbers it
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::KeepaliveTests::test_an_existing_ssh_command_is_left_alone_and_said_so
  - **Verified:** yes (2026-09-09)
- [ ] **AC3** Given the shipped `.githooks/pre-push` driven as a subprocess in the existing hook fixture, when it prints its opening cost estimate, then that output names the keepalive the connection needs across the gate and the command that sets it, on stderr where the pusher reads it. The fixture copies the hook alone and never runs `enable-hooks.sh`, so this criterion is carried by the hook's own text and nothing else
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::KeepaliveTests::test_the_hook_names_the_keepalive_the_gate_needs
  - **Verified:** yes (2026-09-09)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in tools/enable-hooks.sh, delete the `core.sshCommand` write so a fresh clone gets no keepalive | Given a throwaway clone whose LOCAL config carries no `core.sshCommand`, and an environment with `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` POINTED AT `/dev/null` so the developer's own `~/.gitconfig` cannot answer for the clone. Unsetting those two is what LETS it answer, which is the opposite of what this control needs, and pointing them at a null file is the mechanism the module's own git helper already uses, when `bash tools/enable-hooks.sh` runs, then `git config --local core.sshCommand` names an ssh carrying `ServerAliveInterval` and `ServerAliveCountMax`, and the script prints what it set |
| AC2 | in tools/enable-hooks.sh, drop the guard that reads the existing value first, making the write unconditional so it overwrites what the developer set | Given a clone whose LOCAL `core.sshCommand` is already set to something else, when the script runs in the same scrubbed environment, then that value is unchanged and the script says it left it alone. This is the paired control AC1 cannot supply: deleting the write satisfies "an existing one is untouched" trivially, and the likelier careless implementation is an unconditional write that clobbers it |
| AC3 | in .githooks/pre-push, strip the keepalive sentence from the cost line it echoes to stderr | Given the shipped `.githooks/pre-push` driven as a subprocess in the existing hook fixture, when it prints its opening cost estimate, then that output names the keepalive the connection needs across the gate and the command that sets it, on stderr where the pusher reads it. The fixture copies the hook alone and never runs `enable-hooks.sh`, so this criterion is carried by the hook's own text and nothing else |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Filed |
