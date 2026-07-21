# BG0229: verify_ac ts-check reads a missing spec as an empty one and reports a clean matrix, so a typo'd --spec passes as green

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Verification depth:** functional (red-then-green: 6 of 7 new tests failed on the unfixed script, the missing spec having printed 'ts-check: 0 incomplete matrix row(s)' with exit 0; 7 hand-mutants of the guard, the exit code and the unreadable branch all killed)
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`ts_check` reads a non-existent spec file as empty text and then reports a clean AC Coverage Matrix with exit 0. A gate pointed at a moved, renamed or typo'd spec path therefore reports 'every AC is mapped to a passing test case' when it read nothing at all. This is the vacuous-pass family of BG0197 and BG0131: a checker that passes on input it cannot parse reports coverage it does not have, and ts-check exists precisely to stop the AC-to-test matrix being decorative. Found while fixing BG0220 - one draft test there passed for exactly this reason (asserting rc 0 while the spec was never found), which is how it surfaced.

## Steps to Reproduce

Run `verify_ac.py` ts-check --spec sdlc-studio/test-specs/DOES-NOT-EXIST.md. Observed: a clean matrix and exit 0. Expected: a refusal naming the unreadable path, distinct from 'the matrix is complete'.

## Proposed Fix

Refuse an unreadable or absent spec loudly with a non-zero exit, naming the resolved path that was tried. 'Absent' and 'empty but present' are different facts and must not share an exit code. Pin it with a test that asserts the non-zero exit on a missing path, since a test asserting rc 0 is satisfied by the defect itself.

## Resolution

Reproduced first, verbatim: `ts-check --spec <missing>` printed
`ts-check: 0 incomplete matrix row(s) in TS-DOES-NOT-EXIST.md` and exited 0.

`ts_check` now refuses what it could not read, and the two ways of failing to read a spec
are kept apart because their callers differ:

- ABSENT (no such file, or a directory - both read back as empty text) raises
  `FileNotFoundError`. The refusal lives in the library, so no caller can obtain `[]` from
  a spec that is not there; `cmd_ts_check` catches it, names the RESOLVED path on stderr
  and exits 2 - a broken invocation, never 1 (a matrix with findings) and never 0.
- PRESENT but not valid UTF-8 returns a finding naming the file rather than raising, so a
  scanner walking a whole tree still survives one wreck (the non-UTF-8 sweep in
  `test_reconcile.py` asserts exactly that), while the result is non-empty and nothing can
  read it as a passing matrix.

'Present but empty' stays distinct from 'absent': a zero-byte file is readable, so it is
not the refusal path. The summary line now reads `N finding(s)`, not
`N incomplete matrix row(s)`, because an unreadable spec is one finding and no rows at all.

Pinned by `TsCheckAbsentSpecTests` in `scripts/tests/test_verify_ac.py`, 7 cases, every one
asserting a non-zero exit or a raised error - an rc-0 assertion would have been satisfied by
the defect itself. 6 of the 7 were red before the fix. Mutation-proven (bytecode purged,
`python3 -B`), all killed: dropping the absent guard; returning `[]` instead of raising;
`is_file` weakened to `exists` (lets a directory through); exit 1 instead of 2; refusing a
present-but-empty spec too; printing the summary line over a refusal; dropping the
unreadable branch.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
| 2026-07-21 | sdlc-studio | Fixed - absent spec refused with exit 2 naming the resolved path, unreadable spec flagged; 7 mutation-proven tests |
