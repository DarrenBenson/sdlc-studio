# BG0123: The retro gate passes a 0-byte file - it checks the filename, not the retro

> **Status:** Open
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032
> **Raised-by:** sdlc-studio; agent; v1
> **Severity:** High

## Summary

gate.py's retro leg is 'present = bool(list(retros.glob(f"{`retro_id`}*.md")))' - a filename existence check. An empty file named RETRO9999.md yields '[PASS] retro: batch retro RETRO9999 present'. The one ceremony the gate blocks a sprint close on is satisfied by touch. This is LL0008 in the guard itself (a deterministic tool must fail loud, never report success it did not achieve) and LL0015 (a guard that only catches the total case is not a guard): it catches 'no file at all' and nothing else. Root cause is that there is no scripts/retro.py to produce or validate a retro, so the gate has nothing to check but a glob.

## Steps to Reproduce

mkdir -p sdlc-studio/retros && : > sdlc-studio/retros/RETRO9999.md && python3 scripts/gate.py --require-retro RETRO9999   # -> [PASS] retro: batch retro RETRO9999 present

## Proposed Fix

Validate the retro's CONTENT, not its name: required sections present (Delivered, What went well, What was hard, Lessons), at least one lesson, and every finding dispositioned (CR0243). Depends on the deterministic retro spine.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
