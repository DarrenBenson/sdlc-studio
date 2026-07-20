# BG0215: A timed-out mutation run leaves the mutant on disk and the restore captures it

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional (the SIGKILL scenario is reproduced end to end: a stranded mutant plus sidecar is recovered before the baseline and the true original ends the run on disk; the sidecar is proven to hold the original while the mutant is applied and to clear on restore; a clean run reports no recovery; an unreadable sidecar refuses with the git remedy named)
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

mutation.py and hand-rolled mutation harnesses write the mutant into the working tree and restore it afterwards. If the run is killed mid-flight (timeout, interrupt), the mutant survives. A subsequent cp-based restore then copies the MUTANT into the backup, so every later run measures mutated code while reporting on the original. Observed during EP0087: a gate.py mutant survived a 2-minute timeout, was captured by the backup, and the next baseline came back FAILED - which reads as a code regression, not a corrupted harness.

## Steps to Reproduce

1. Run a mutation harness that does cp file file.bak, mutates, runs tests, restores. 2. Kill it during the test run (timeout). 3. The mutant is still on disk. 4. Re-run the harness: it copies the mutant into file.bak. 5. Baseline now fails and the failure looks like a real regression.

## Proposed Fix

Restore from a source the mutant cannot have touched (git checkout, or a copy taken before the first mutation), and ALWAYS re-run the unmutated baseline first - a baseline that is not green means the harness is lying, not the code. Consider a trap/finally that restores on signal, and refuse to start when the working tree is already dirty for the target file.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
