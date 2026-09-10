# BG0654: A push whose pre-push gate outlives the SSH connection git opened before the hook dies with exit 141 after the gate reports PASS, and nothing names the cause

> **Status:** Fixed
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
- [ ] **AC3** Given the shipped `.githooks/pre-push` DRIVEN as a subprocess by the module's own push fixture, when the push runs, then the hook's stderr - the stream git shows a pusher - names the keepalive the connection needs across the gate and the command that sets it. Read from the driven hook's output rather than from its source: a sentence present in the file but wrapped in a false branch satisfies a text search and reaches no pusher, which is what the first selector here accepted
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::KeepaliveTests::test_the_hook_names_the_keepalive_the_gate_needs
  - **Verified:** no

- [ ] **AC4** Given a clone whose GLOBAL `core.sshCommand` is set - which is where a user, an identity file or a port usually lives - when the script runs, then that value is left in force and the script says so. Reading only the local scope shadows it, and writing a bare ssh over it strips the identity silently, so the next push fails to authenticate for a reason nothing names. AC1 and AC2 both point the outer config files at a null file, so neither can tell the safe implementation from the harmful one
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::KeepaliveTests::test_a_global_ssh_command_is_not_shadowed_by_the_local_write
  - **Verified:** no
- [ ] **AC5** Given a push the red-CI read REFUSES, when the hook runs, then the keepalive advice has already been printed. That block exits before the cost line, and the pusher whose connection is about to drop is exactly the one who retries - so advice printed after it reaches only the pushes that get as far as paying for the gate
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::KeepaliveTests::test_the_keepalive_reaches_a_push_the_red_ci_read_refuses
  - **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in tools/enable-hooks.sh, delete the `core.sshCommand` write so a fresh clone gets no keepalive | Given a throwaway clone whose LOCAL config carries no `core.sshCommand`, and an environment with `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` POINTED AT `/dev/null` so the developer's own `~/.gitconfig` cannot answer for the clone. Unsetting those two is what LETS it answer, which is the opposite of what this control needs, and pointing them at a null file is the mechanism the module's own git helper already uses, when `bash tools/enable-hooks.sh` runs, then `git config --local core.sshCommand` names an ssh carrying `ServerAliveInterval` and `ServerAliveCountMax`, and the script prints what it set |
| AC2 | in tools/enable-hooks.sh, drop the guard that reads the existing value first, making the write unconditional so it overwrites what the developer set | Given a clone whose LOCAL `core.sshCommand` is already set to something else, when the script runs in the same scrubbed environment, then that value is unchanged and the script says it left it alone. This is the paired control AC1 cannot supply: deleting the write satisfies "an existing one is untouched" trivially, and the likelier careless implementation is an unconditional write that clobbers it |
| AC3 | in .githooks/pre-push, wrap the keepalive echo in `if false; then ... fi`, so the sentence is present in the file and no pusher ever sees it | Given the shipped `.githooks/pre-push` driven as a subprocess in the existing hook fixture, when it prints its opening cost estimate, then that output names the keepalive the connection needs across the gate and the command that sets it, on stderr where the pusher reads it. The fixture copies the hook alone and never runs `enable-hooks.sh`, so this criterion is carried by the hook's own text and nothing else |
| AC4 | in tools/enable-hooks.sh, narrow the precondition to the local scope | Given a clone whose GLOBAL `core.sshCommand` is set - which is where a user, an identity file or a port usually lives - when the script runs, then that value is left in force and the script says so. Reading only the local scope shadows it, and writing a bare ssh over it strips the identity silently, so the next push fails to authenticate for a reason nothing names. AC1 and AC2 both point the outer config files at a null file, so neither can tell the safe implementation from the harmful one |
| AC5 | in .githooks/pre-push, move the keepalive echo back below the red-CI acknowledgement block | Given a push the red-CI read REFUSES, when the hook runs, then the keepalive advice has already been printed |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Filed |
| 2026-09-09 | Claude Fable 5.1 | Delivery review, product seat: REJECT, and the finding was real and harmful. The precondition read `git config --local --get`, so a developer's GLOBAL ssh command was shadowed rather than respected: the script announced it had SET a bare keepalive while the user, identity file and port that global value carried were gone, and the next push would fail to authenticate for a reason nothing named. Both shipped claims - AGENTS.md's and the changelog's - were false for that case. It reads the EFFECTIVE value now and names the scope it found it in, and AC4 pins it, because AC1 and AC2 both null out the outer config files and so cannot tell the safe implementation from the harmful one |
| 2026-09-09 | Claude Opus 5 | Round two, all three seats. AC3's selector asserted on the hook's SOURCE TEXT while its criterion says the pusher reads the line on stderr: a reviewer wrapped the echo in `if false; then ... fi` and the shipped node stayed green. It drives the module's own push fixture now, and both mutants - the false branch and the deleted echo - are killed. The engineering seat also found the line printed AFTER the red-CI acknowledgement block, which exits: a push refused for an unacknowledged red main never saw it, and the pusher whose connection is about to drop is exactly the one who retries. Moved above that block, pinned by AC5 |
| 2026-09-09 | Claude Opus 5 | Two rulings from round two, neither a code change. The keepalive pair shipped is ServerAliveInterval=60 with ServerAliveCountMax=10, not the 20 and 60 the Evidence field records from the retry that landed the push: 60 seconds is well inside the roughly 480-second idle timeout the Summary measures, and ten missed replies is ten minutes of silence before the connection is judged dead, which outlasts the gate. A developer whose GLOBAL ssh command carries no keepalive gets the advice and no setting - AC4 legislates that deliberately, because a command somebody chose is not something this script overwrites, and AGENTS.md now says so in the same sentence. AC3's line stays unconditional: the hook cannot read the pusher's effective config cheaply, and one line on a push that already prints three is not worth a config read |
