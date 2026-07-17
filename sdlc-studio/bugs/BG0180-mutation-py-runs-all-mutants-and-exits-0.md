# BG0180: mutation.py runs all mutants and exits 0 after a red baseline

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

During the RUN-01KXPJG9 close, a mutation run against a dirty tree (a stranded mutant from a killed prior run) recorded baseline:fail - and then still applied all 25 mutants (every one 'error - baseline red'), wrote the worthless report, and EXITED 0. A red baseline means the run can prove nothing: it should refuse immediately after the baseline check, exit non-zero, and name the remedy (clean the tree / fix the suite). Also observed: a killed run (SIGTERM via TaskStop) left its in-flight mutant applied to the working tree - a signal handler or atexit restore for the currently-applied mutant would have prevented the whole incident.

## Steps to Reproduce

1. make the target suite red (any failing test); 2. mutation.py run --files <target> --test <suite>; 3. observe: all mutants applied and errored, report written, exit code 0. For the strand: kill the process mid-mutant and diff the tree

## Proposed Fix

Refuse after a red baseline (non-zero exit, no mutants applied, remedy named); restore the applied mutant on SIGTERM/atexit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
