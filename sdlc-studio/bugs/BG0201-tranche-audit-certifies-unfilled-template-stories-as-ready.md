# BG0201: tranche audit certifies unfilled template stories as ready: _weak_ac only detects one hardcoded phrase

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; proven against the live 32-unit batch)
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/audit.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

audit.py `_weak_ac` is documented as flagging 'no checkable AC, or the tautology placeholder', but TAUTOLOGY is the single literal string 'lint and tests green'. The template placeholders artifact.py new actually emits ({{define}}, {{context}}, {{action}}, {{outcome}}, {{executable check}}) match nothing, so a story that is pure unexpanded template passes the readiness check. Proven: all 28 Draft stories in RUN-01KXVYGR return `_weak_ac`=False and 'audit check' reported 32/32 ready over them. This is the step-2 gate whose stated purpose is that work never starts on a unit that would pass the downstream gates vacuously; `verify_ac` would then run '{{executable check}}' as the unit's own oracle. Same class as BG0193 (a verifier exiting 0 having run nothing) and L-0098.

## Steps to Reproduce

1. Scaffold a story with artifact.py new --type story (ACs land as '### AC1: {{define}}' with '- **Verify:** {{executable check}}'). 2. Run audit.py check --ids <that story>. 3. Observe 'ready'. 4. Confirm directly: import audit; `audit._weak_ac(path.read_text())` returns False.

## Proposed Fix

Detect an unexpanded template placeholder generally: flag any AC item still containing a '{{...}}' span, in addition to the existing TAUTOLOGY phrase. Keep the phrase check (a filled-in-but-vacuous AC is a different failure), and add a regression test asserting a freshly scaffolded story is NOT ready.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
