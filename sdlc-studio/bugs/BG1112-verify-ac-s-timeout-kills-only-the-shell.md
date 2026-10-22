# BG1112: verify_ac's timeout kills only the shell it started, so a timed-out shell or eval verifier leaves its real test runner (npx, vitest, pytest) running as an orphan that keeps writing into the workspace

> **Status:** Open
> **Created:** 2026-10-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Severity:** Medium
> **Points:** 2

## Summary

Found in a consuming project (a unit review, 2026-10-21). `verify_ac.py` runs a shell or eval Verify line with subprocess.run(cmd, shell=True, timeout=...) (scripts/`verify_ac.py` ~477 for eval, ~521 for the verb runners). On TimeoutExpired, subprocess.run kills only its direct child, the /bin/sh, and the commands under it (npx, then vitest and its worker forks) are re-parented and keep running. In that project the orphaned vitest ran on after `verify_ac` had recorded exit 124 and wrote a `node_modules`/.vite results cache into a review worktree, which the reviewer had to find and remove. A long gate run (reconcile --verify, gate.py --release) that times out several verifiers can leave several runners competing for CPU with the verifiers that follow, which makes later timing-sensitive criteria slower and so more likely to time out too. mutation.py fixed the same class with a new session plus os.killpg (BG0410). `verify_ac` never adopted it.

## Steps to Reproduce

Write a criterion whose Verify line is shell sh -c 'sleep 300 & wait' (or a slow npx vitest run) and run `verify_ac.py` with --timeout 2. `verify_ac` reports exit 124 after 2 s, and ps still shows the sleep (or vitest) running minutes later, re-parented to init.

## Proposed Fix

Start every verifier subprocess in its own session (`start_new_session`=True on POSIX) and, on TimeoutExpired, os.killpg the whole group (SIGTERM, a short grace, then SIGKILL) before returning the 124 result. Reuse mutation.py's BG0410 helper rather than writing a second one. On platforms without process groups, keep today's behaviour and say so in the help.

## Acceptance Criteria

- [ ] **AC1** When a shell or eval verifier times out, `verify_ac` reports exit 124 and no process from that verifier's tree is still running when it returns
  - **Verify:** shell python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests -k timed_out_verifier_leaves_no_process

## Impact

A timed-out verifier keeps running and writing after the gate has judged it, contending with later verifiers and leaving files in the workspace that nobody asked for.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-21 | sdlc-studio | Created via `new` (deterministic) |
