# BG0125: grep verifier: the documented path_glob example false-REDs (verb has zero test coverage)

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/reference-verify.md

## Summary

The grep Verify verb runs as an argv list (no shell), so a shell glob like src/**/*.ts is passed LITERALLY to rg/grep. reference-verify.md:105's canonical example 'grep "export class AuthClient" src/**/*.ts' therefore fails on code that is genuinely present - a false-RED that blocks a legitimate story -> Done. The verb has zero tests in `test_verify_ac.py`, which is why the doc-vs-behaviour gap survived.

## Steps to Reproduce

Story AC: '- **Verify:** grep "export class AuthClient" src/**/*.ts' with the class present at src/auth/client.ts. Run: `verify_ac.py` run --story story.md --dry-run  ->  FAIL AC1 (rg: src/**/*.ts: No such file or directory). Same check with 'src/' (directory form) PASSES. Reproduced through the CLI.

## Proposed Fix

Either drop ** from the doc/comment (use the recursing directory form 'src/'), or expand trailing path args with glob before invoking the tool. Add grep-verb tests for the multi-path and no-match cases (LL0010: the fix's test must fail against today's behaviour).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
