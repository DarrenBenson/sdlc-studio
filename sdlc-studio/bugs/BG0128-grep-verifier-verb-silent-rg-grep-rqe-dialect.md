# BG0128: grep verifier verb: silent rg/grep -rqE dialect swap makes a verdict environment-dependent

> **Status:** Open
> **Severity:** Low
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/reference-verify.md

## Summary

`verify_ac.py`:344 picks 'rg -q' when ripgrep is on PATH, else 'grep -rqE' - different regex dialects (Rust regex vs POSIX ERE). A Verify line using \d, \w, \b, (?:...), non-greedy, or lookahead can yield a DIFFERENT pass/fail verdict on the same story depending only on whether rg is installed (dev box with rg vs CI runner without). For a gate whose value is a deterministic verdict, the engine is an undeclared invisible input. Low because GNU grep masks it on many boxes; BSD/macOS/busybox grep does not.

## Steps to Reproduce

A Verify grep pattern using \d on a host with rg vs a host with only BSD grep can disagree. reference-verify.md:105 treats 'rg -q (or grep -rqE)' as interchangeable; they are not.

## Proposed Fix

Commit to one engine (prefer rg; fail loud with 'install ripgrep' when absent rather than silently swapping), or document the POSIX-ERE-only constraint prominently.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
