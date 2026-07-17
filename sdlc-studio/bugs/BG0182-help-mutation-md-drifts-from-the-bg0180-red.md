# BG0182: help/mutation.md drifts from the BG0180 red-baseline-refuse fix

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/mutation.md
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Delivered-by:** claude-opus-4-8

## Summary

help/mutation.md (~L37, L52) still describes the pre-BG0180 behaviour - a red baseline records an error per mutation and the run continues. BG0180 changed this: a red/broken baseline now refuses (no mutant applied, refused+remedy in the report, exit 2). The help must describe the refuse-on-red contract.

## Steps to Reproduce

Read help/mutation.md around L37 and L52; compare with mutation.py `cmd_run`'s refuse-on-red-baseline path and BG0180.

## Proposed Fix

Rewrite the two passages to describe: a red or broken baseline REFUSES (no mutant applied, refused+remedy in report, non-zero exit), and stranded mutants are restored on SIGTERM/atexit.

## Resolution

Rewrote step 2 and the `error` verdict in `help/mutation.md` to the shipped BG0180 contract: a red or broken baseline REFUSES the whole run (no mutant applied, report marked `refused` with the remedy, non-zero exit), and a red baseline no longer reaches the per-mutation `error` state. Added the stranded-mutant restore note (atexit + SIGTERM handler). Verified against `mutation.py` `cmd_run` (the refuse-on-red path) and the `_install_restore_handlers` implementation.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
| 2026-07-17 | claude-opus-4-8 | Fixed: help/mutation.md matches the refuse-on-red contract |
