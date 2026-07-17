# BG0164: An attempts-only telemetry record never stamps Delivered-by on the artefact - the escalation case loses the audit attribution the stamp exists for

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a
> **Delivered-by:** claude-opus-4-8

## Summary

record() (telemetry.py:296) calls `stamp_delivery` only when the record carries a flat `model`. The blessed shape for an escalated unit is an attempts list with no flat model (exactly what US0172's tests record), so the unit that most needs model attribution - one delivered by escalation - silently gets no '> **Delivered-by:**' stamp. The module's own comment says the stamp exists because 'which model delivered a change is audit information', and retro.accuracy was patched the same sprint to derive the delivering model as attempts[-1].model - so the codebase holds 'delivering model = last attempt' in a reader but not the writer (LL0016), and the omission is silent because stamping is best-effort. Reproduced by the panel: attempts-only record -> stamped=False; same record with flat model -> stamped=True. No test covers stamping from attempts. One-line fix. Verified 3x.

## Steps to Reproduce

tel.record(root, {"id": "US0001", "type": "story", "attempts": [{"model": "claude-haiku-4-5", "tokens": 1}, {"model": "claude-opus-4-8", "tokens": 2}]}) against an existing US0001 artefact - no Delivered-by line appears; the same record with a flat model stamps.

## Proposed Fix

When flat model is absent, derive the stamp model from `attempts_of(rec)[`-1].model (matching retro's delivering-model rule); add a stamp assertion to the attempts-shape test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
