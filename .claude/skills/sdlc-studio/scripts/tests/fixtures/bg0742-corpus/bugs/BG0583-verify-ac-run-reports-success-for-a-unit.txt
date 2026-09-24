# BG0583: verify_ac run reports success for a unit it never read

> **Status:** Open
> **Severity:** High
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

## Acceptance Criteria

- [ ] **AC1** Given `verify_ac.py run --ids <id>` naming an id with no unit file, when it runs, then it exits non-zero
- [ ] **AC2** Given `verify_ac.py run --story <id-shaped value>` that resolves to no file, when it runs, then it exits non-zero
- [ ] **AC3** Given a `--ids` run where every id resolves, when it runs, then it still exits 0 - the positive control, so the fix is not a blanket refusal

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
