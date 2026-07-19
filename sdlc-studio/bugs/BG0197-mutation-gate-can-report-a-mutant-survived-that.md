# BG0197: mutation gate can report a mutant SURVIVED that never ran, via stale .pyc

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; both guards mutation-proven)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py
> **Created:** 2026-07-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`mutation._run_tests` spawns the test command with no PYTHONDONTWRITEBYTECODE and no `__pycache__` purge. CPython invalidates a .pyc on (source mtime, source size), so a mutant that is the SAME byte length as the original and is written within the same mtime second as a previous run reuses the stale bytecode: the ORIGINAL code executes, the tests pass, and the mutant is recorded as SURVIVED. Same-length mutants are the common case for operator-swap fault classes. The gate's headline kill rate is therefore evidence about the bytecode cache, not only about the tests - the same class of unearned result the mutation gate exists to expose. Found while hand-mutating lib/`sdlc_md.py` during BG0194: a v3/v2 alternation swap (identical length) reported killed, then reported OK after restore, because neither run recompiled.

## Steps to Reproduce

1. Pick a source file and a fast test module that imports it. 2. Run the tests once so `__pycache__` is written. 3. Within the same second, replace the source with a mutant of IDENTICAL byte length. 4. Re-run the tests in the same interpreter session family. 5. Observe the tests pass - confirm by printing the compiled object (e.g. a regex .pattern) that the ORIGINAL source is in effect. 6. rm -rf `__pycache__` and re-run: the mutant now fails as it should.

## Proposed Fix

Run the mutant test command with PYTHONDONTWRITEBYTECODE=1 in its environment, and/or purge `__pycache__` under the mutated file's tree between the baseline run and each mutant run. Prefer both: the env var stops new writes, the purge clears what a prior non-mutation run already cached. Add a regression test that applies a same-length mutant immediately after a baseline run and asserts it is killed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Filed |
