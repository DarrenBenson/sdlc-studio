# BG0410: The mutation run's temp-file sink stopped the hang by orphaning the child, and leaks an fd and a temp file whenever Popen fails

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Evidence:** Round-2 independent review of commit 06c806d7, mutant M3 killed but three new defects measured. Repair 9 of the nine stop-ships.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** round-2 independent review; human; v1

## Summary

Replacing the pipe with a temp-file sink removed the 600s-per-mutant hang, and that part is verified: repaired 0.00s against 5.006s with the pipe restored. But the hang did not stop happening - it stopped being OBSERVED, and the cleanup it used to trigger stopped running.

With a pipe, a backgrounded child held the read open to the timeout, and the timeout branch called `os.killpg` on the whole session. With a file, `proc.wait()` returns as soon as the direct child exits and the group is NEVER killed on the normal path - `os.killpg` appears only inside the `except subprocess.TimeoutExpired` branch, which this change made unreachable for exactly the case it was written for.

Measured: `_run_tests("(sleep 8; touch MARKER) & echo 'FAILED tests/t.py::C::t'; exit 1")` returns `fail` immediately, and ten seconds later the orphan has run to completion. `run_gate` calls `_run_tests` once per mutant, so a suite that backgrounds anything leaves N orphans per run. Against the dev-server case this function's own docstring names, mutant 2 onward binds a port already held and every verdict after the first is garbage.

The docstring still asserts "the whole process GROUP is killed on timeout". Still true, and now only on a path this change made unreachable.

Two smaller defects on the same lines. `tempfile.mkstemp` (line 983) and `subprocess.Popen` (984) sit OUTSIDE the `try` that begins at 993, so any Popen failure leaks both: five calls with a nonexistent cwd raised FileNotFoundError five times, took /proc/self/fd from 4 to 9, and left five /tmp/`mutation_run_`* files. And `os.close(sink_fd)` and `os.unlink(sink)` share one `contextlib.suppress(OSError)`, so a raising close silently skips the unlink.

Separately, `_OUTPUT_CAP` (line 915) is dead - one occurrence in the file, its own definition. Its docstring asserts it bounds the retained transcript; `_read_tail` hardcodes `512 * 1024` as its default instead. Two sources of truth, one decorative.

## Steps to Reproduce

1. `_run_tests` with a command that backgrounds a child and exits: the call returns at once and the child survives.
2. Read mutation.py:983-1007 - `mkstemp` and `Popen` precede the `try:` at 993; `os.killpg` appears only in the TimeoutExpired branch.
3. Call `_run_tests` five times with `cwd` set to a nonexistent path; count `/proc/self/fd` entries and `/tmp/mutation_run_*` before and after.
4. `grep -c _OUTPUT_CAP mutation.py` returns 1.

## Proposed Fix

1. Kill the group unconditionally after `wait()` returns, not only on timeout - the direct child having exited says nothing about what it launched. Reap the session on both paths.
2. Move `mkstemp` and `Popen` inside the `try`, or wrap the whole body in `try/finally`, so a construction failure cannot leak the fd or the file.
3. Give `os.close` and `os.unlink` their own suppress each, so a raising close cannot skip the unlink.
4. Either make `_read_tail` default to `_OUTPUT_CAP` or delete the constant. A constant whose docstring claims an effect it does not have is worse than no constant.
5. Correct the `_run_tests` docstring: say on which paths the group is killed.

## Acceptance Criteria

- [ ] A test asserts that a command backgrounding a child leaves no surviving process once `_run_tests` returns, on the NORMAL exit path and not only on timeout.
- [ ] A test asserts that a `_run_tests` call whose Popen fails leaks neither a file descriptor nor a `/tmp/mutation_run_*` file.
- [ ] A raising `os.close` does not prevent the `os.unlink`.
- [ ] `_OUTPUT_CAP` is either read by `_read_tail` or removed; no constant claims an effect it does not have.
- [ ] The `_run_tests` docstring states which exit paths kill the process group, and matches the code.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | round-2 independent review | Filed |
