# BG0166: ADR-010's documented opt-out lessons.loop: judgement disarms only one of the three close lanes it claims to make advisory - lessons-summary and lessons-validity block regardless

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, sdlc-studio/trd.md, sdlc-studio/prd.md, .claude/skills/sdlc-studio/reference-config.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a
> **Delivered-by:** claude-opus-4-8

## Summary

TRD ADR-010 says 'Bound close-gate lanes enforce it; lessons.loop: judgement makes them advisory' (plural), prd.md:480 promises 'judgement makes the retro/lessons close lanes advisory', and reference-config.md says judgement 'reports, never blocks'. In gate.py only `_retro_present` reads the config (mode != 'judgement' -> blocking); `_lessons_summary` and `_lessons_validity` hard-code blocking: True on every return path and never read lessons.loop (nor do lessons.py's status functions), while all three are bound as one set under --require-retro. An operator who records the documented opt-out still has the close blocked by two of the three lanes - the key silently covers a third of what three documents say it covers. The retro lane's own comment condemns a documented-but-unread opt-out as 'the very disease this loop exists to cure'. The sole opt-out test covers just the retro lane. Fix in code (honour the key) or docs (re-scope the claim) - code preferred given three docs promise the plural. Verified 3x.

## Steps to Reproduce

Set lessons.loop: judgement in .config.yaml; run gate --require-retro in a workspace where the lessons summary or validity lane fails - the gate still blocks (both lanes hard-code blocking: True); only the retro-present lane went advisory.

## Proposed Fix

Honour lessons.loop in `_lessons_summary` and `_lessons_validity` (same mode -> blocking derivation as `_retro_present)`, extend TheOptOutIsHonoured tests to all three lanes - or, if two lanes are meant to stay hard, correct ADR-010, prd.md:480 and reference-config.md to say so explicitly.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
