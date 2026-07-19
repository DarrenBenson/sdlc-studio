# CR-0336: Gate mutation lane should surface BG0180's refused state

> **Status:** Complete
> **Decomposed-into:** EP0072
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The advisory mutation lane in gate.py reads a mutation report but does not surface BG0180's new 'refused' state (red/broken baseline). A refused report reads as 0/0 (no signal).

## Impact

Operators reading the gate cannot distinguish a clean mutation run from a refused one (red baseline); the advisory lane silently under-reports.

## Acceptance Criteria

- [ ] The mutation lane prints a distinct 'refused (red baseline)' line when the report's baseline is not pass, rather than 0/0.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
