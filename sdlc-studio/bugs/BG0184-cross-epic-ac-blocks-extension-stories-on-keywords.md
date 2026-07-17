# BG0184: cross-epic-ac blocks extension stories on keywords owned by a terminal epic

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/audit.py, .claude/skills/sdlc-studio/scripts/ac_scope.py
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

audit.py maps cross-epic-ac to a blocking issue and `ac_scope.check` has no terminal-owner filter, so a new extension story reusing a keyword owned by an already-terminal epic is silently blocked NOT-READY - a false planning-gate block (was CR0331).

## Steps to Reproduce

Create a story whose AC reuses a keyword scoped to a Done/terminal epic; run the tranche audit / `ac_scope.check` - it flags cross-epic-ac and blocks readiness though the owning epic is closed.

## Proposed Fix

`ac_scope.check` should exempt keywords owned by a TERMINAL epic (a closed epic no longer owns live scope), or scope the cross-epic-ac block to non-terminal owners only. Add a terminal-owner regression test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
