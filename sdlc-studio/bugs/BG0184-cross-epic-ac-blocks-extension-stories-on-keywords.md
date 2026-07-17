# BG0184: cross-epic-ac blocks extension stories on keywords owned by a terminal epic

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/audit.py, .claude/skills/sdlc-studio/scripts/ac_scope.py
> **Delivered-by:** claude-opus-4-8
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

audit.py maps cross-epic-ac to a blocking issue and `ac_scope.check` has no terminal-owner filter, so a new extension story reusing a keyword owned by an already-terminal epic is silently blocked NOT-READY - a false planning-gate block (was CR0331).

## Steps to Reproduce

Create a story whose AC reuses a keyword scoped to a Done/terminal epic; run the tranche audit / `ac_scope.check` - it flags cross-epic-ac and blocks readiness though the owning epic is closed.

## Proposed Fix

`ac_scope.check` should exempt keywords owned by a TERMINAL epic (a closed epic no longer owns live scope), or scope the cross-epic-ac block to non-terminal owners only. Add a terminal-owner regression test.

## Resolution

`ac_scope.check` now reads each epic's status and builds a `terminal_epics` set; a keyword whose
sole owner is terminal is dropped from `distinctive` before the story pass, so it never flags. A
live (non-terminal) owner is unchanged and still flags. Verified functionally: re-running the
tranche audit on US0201/US0204/US0206 (which reused `loop`/`incremental`/`testing`, all owned by
Done epics EP0010/EP0036/EP0004) cleared their false NOT-READY block. Regression tests
`test_terminal_owner_epic_exempted` and `test_live_owner_epic_still_flags` pin both directions.
`audit.py` needed no change - it consumes `ac_scope.check`'s output, which is now correct at source.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
| 2026-07-17 | claude-opus-4-8 | Fixed: terminal-owner exemption in ac_scope; regression tests added |
