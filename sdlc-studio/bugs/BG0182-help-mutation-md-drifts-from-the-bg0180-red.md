# BG0182: help/mutation.md drifts from the BG0180 red-baseline-refuse fix

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/mutation.md
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

help/mutation.md (~L37, L52) still describes the pre-BG0180 behaviour - a red baseline records an error per mutation and the run continues. BG0180 changed this: a red/broken baseline now refuses (no mutant applied, refused+remedy in the report, exit 2). The help must describe the refuse-on-red contract.

## Steps to Reproduce

Read help/mutation.md around L37 and L52; compare with mutation.py `cmd_run`'s refuse-on-red-baseline path and BG0180.

## Proposed Fix

Rewrite the two passages to describe: a red or broken baseline REFUSES (no mutant applied, refused+remedy in report, non-zero exit), and stranded mutants are restored on SIGTERM/atexit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
