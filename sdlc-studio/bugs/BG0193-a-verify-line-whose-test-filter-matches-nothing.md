# BG0193: a Verify line whose test filter matches nothing passes vacuously

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`verify_ac` treats exit 0 as AC-met, but 'python3 -m unittest discover -k <pattern>' exits 0 having run ZERO tests when the pattern matches nothing. A renamed or deleted test class silently converts a real AC into a green no-op, and the same applies to pytest -k and any filtered runner. The verifier cannot distinguish 'the assertion held' from 'no assertion ran' - the exact false-green class the mutation gate exists to prevent.

## Steps to Reproduce

1. Author an AC with 'Verify: shell python3 -m unittest discover -s tools/tests -p `test_gate_timing.py` -k NoSuchTests'. 2. Run `verify_ac` run --id <story>. 3. Observe the AC recorded as passed. 4. Confirm the underlying command reports 'Ran 0 tests' and exits 0.

## Proposed Fix

Parse the runner's test count from its output and fail an AC whose verifier ran zero tests, or have `verify_ac` lint flag a filtered invocation (-k/-m/::) that resolves to no tests. At minimum surface a 'vacuous verifier' warning alongside the existing weak-verify lint.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Filed |
