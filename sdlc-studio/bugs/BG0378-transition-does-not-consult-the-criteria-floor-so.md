# BG0378: transition does not consult the criteria floor, so the terminal status is set and only the commit that records it is refused

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (closing BG0370, RUN-01KYKVZM); agent; skill v5.0.0

## Summary

BG0370 closed the criteria floor at the validate layer, which the pre-commit gate enforces, so a bug can no longer LAND at a terminal status with no acceptance criteria. The transition verb itself still performs the change: it checks verification depth and triage separation and never asks whether the unit has a criterion. The artefact is therefore mutated on disk and the refusal arrives later, from a different tool, phrased as a validation error rather than as a blocked transition. Defence at the gate rather than at the verb, which is weaker than the rule reads and leaves the working tree in the state the rule forbids.

## Steps to Reproduce

Observed while closing BG0370 on a fresh project. transition set <bug> Fixed on a bug carrying only the auto-written stated absence succeeds and writes the status; validate check then reports no-ac as an error against the same file.

## Proposed Fix

Add the criteria floor to the transition requirements for a terminal target, reading the same predicate validate uses rather than a second copy, so the refusal happens where the change is attempted and names the missing criteria alongside the other blocked requirements.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: none of its prose fields carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (closing BG0370, RUN-01KYKVZM) | Filed |
