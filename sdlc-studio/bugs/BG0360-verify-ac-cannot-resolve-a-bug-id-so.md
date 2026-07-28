# BG0360: verify_ac cannot resolve a bug id, so no bug can prove its own acceptance criteria

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

Three lanes hit this independently. `verify_ac run --id` resolves stories only, so a bug carrying authored acceptance criteria cannot run them. This sprint's own return rule - a lane verifies its unit before returning - is therefore unrunnable for every bug in the batch, and BG0352's lane correctly returned BLOCKED rather than claim a verification it could not perform. It also means the AC-verify Done gate, the release lane's unspecified-AC refusal and the close reconcile all speak only for stories.

## Steps to Reproduce

Reported by a delivery lane during RUN-01KYKVZM; see the summary for the measurement.

## Proposed Fix

See the summary; the remedy is stated with the defect.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Filed |
