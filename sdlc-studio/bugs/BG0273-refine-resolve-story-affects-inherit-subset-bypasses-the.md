# BG0273: refine resolve_story_affects inherit:subset bypasses the parent-declares-none refusal and never checks the subset is within the parent's Affects; bare 'inherit' is matched case-sensitively so INHERIT falls through to the explicit path

> **Status:** Open
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Severity:** Medium
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |

## Acceptance Criteria

- [ ] refine refuses it, and bare INHERIT in any case is treated as the inherit token
- **Given** a story declares inherit:subset against a request that declares no Affects, or a subset outside the parent's Affects
- **Then** refine refuses it, and bare INHERIT in any case is treated as the inherit token
- **Verify:** manual
