# BG0583: verify_ac run reports success for a unit it never read

> **Status:** Won't Fix
> **Severity:** High
> **Verification depth:** functional (the premise was re-measured through the shipped CLI with the exit code read DIRECTLY rather than after a pipe: five invocations, every one exits as it should)
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-08-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`verify_ac.py run` exits 0 on two inputs it verified nothing for, so the command this repository leans on to prove criteria are red or green reports GREEN for a unit whose file it never opened. `--story <id>` with no matching file under the stories directory prints 'no story file at <id>' and exits 0. `--ids <id>` with no unit file prints a line beginning `error:` and ALSO exits 0, contradicting its own help text, which promises 'an id with no story file is an error'. A caller reading the exit code - which is every script, hook and lane that calls it - cannot distinguish 'all criteria passed' from 'I could not find the unit'.

## Steps to Reproduce

Measured 2026-08-16 at ba8ac72e. 1. `verify_ac.py run --story US9999` (no such story) prints `no story file at US9999, and no story with that id under sdlc-studio/stories` and exits 0. 2. `verify_ac.py run --ids US9999` prints `error: --ids names 1 id(s) with no unit file under sdlc-studio/stories or its sibling bugs/: US9999` and exits 0. 3. The contrast that proves this is a branch rather than a policy: `verify_ac.py run --story NOSUCHID9999` - NOT id-shaped, so treated as a path - exits 2 correctly, and `--id BG0490` exits 1. So the silent-pass is reached precisely by a WELL-FORMED id that does not resolve, which is the input a typo or a renamed unit produces. 4. Found while measuring this run's red-now ledger: `--story BG0490` (a real bug, but not a story) reported nothing and exited 0, and the two bugs were nearly recorded as unmeasured when their 7 criteria were in fact all red.

## Proposed Fix

Both paths must exit non-zero when no unit was read. `--ids` already computes the unmatched set and prints it as an `error:` - it must return 2 rather than falling through to the success return, and the fix should be pinned by a test that asserts the EXIT CODE, not the message, because the message is already correct and the defect survived beside it. `--story` should refuse an id-shaped value that resolves to no file, in the same way it already refuses a path that does not exist; if resolving a bug id under the stories directory is to keep printing a hint, the hint must accompany a refusal rather than a success. Consider whether `run` should resolve a bug id the way `--ids` does (it reads `bugs/` as a sibling), which would have made this invocation work rather than merely fail loudly.

## WON'T FIX - the premise is false, and the measurement that produced it was

Re-measured 2026-08-17 at 8f7819cc, reading each exit code directly instead of after a pipe:

| invocation | exit |
| --- | --- |
| `run --story US9999` (no such story) | 2 |
| `run --story BG0490` (a bug, not a story) | 2 |
| `run --ids US9999` (unmatched) | 2 |
| `run --story NOSUCHID9999` (not id-shaped) | 2 |
| `run --ids BG0582` (resolves, all criteria green) | 0 |
| `run --ids US0625` (resolves, criteria red) | 1 |

So the contract is exactly right and always was: 0 green, 1 red, 2 could-not-read. Every branch
in `cmd_run` returns 2 for an unresolvable scope, and `_scoped_paths` returns a refusal that the
caller prints as `error:` before returning 2.

**The defect was in the measurement.** The original reading was taken as
`verify_ac.py run --story US9999 2>&1 | tail -2; echo "exit=$?"` - and `$?` after a pipeline is
the exit code of `tail`, which succeeds whatever the tool did. Every "exit 0" in the Steps to
Reproduce above is tail's.

The lesson already exists and is already general: **L-0277** - "reading a command's verdict
through a pipe reports the pipe's status. Redirect, then echo the code separately." Nothing about
it needed widening. It was read and not followed, which is precisely the failure mode AGENTS.md
opens by naming, and the cost this time was a High bug filed against a contract that was correct
in every branch.

Filed and refuted in the same session. Left as a record rather than deleted, because a
false-premise filing that quietly disappears teaches nobody what produced it.

## Acceptance Criteria

- [ ] **AC1**  Given `verify_ac.py run --ids <id>` naming an id with no unit file, when it runs, then it exits non-zero
- [ ] **AC2** Given `verify_ac.py run --story <id-shaped value>` that resolves to no file, when it runs, then it exits non-zero
- [ ] **AC3** Given a `--ids` run where every id resolves, when it runs, then it still exits 0 - the positive control, so the fix is not a blanket refusal

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
