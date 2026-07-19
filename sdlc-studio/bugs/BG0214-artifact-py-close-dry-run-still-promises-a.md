# BG0214: artifact.py close --dry-run still promises a close the real run refuses

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0213 made transition's dry-run honest, but artifact.py close --dry-run returns its preview BEFORE reaching transition, so it never evaluates the gates. On a bug with no parseable Verification depth field, 'artifact.py close --id BG0001 --dry-run' prints 'would close BG0001' while 'transition.py set --id BG0001 --status Fixed --dry-run' correctly reports the refusal. Two pre-flights over the same transition give opposite answers, and the one an agent is likelier to reach for is the wrong one. Pre-existing rather than introduced by BG0213 - but BG0213's framing called transition's dry-run 'the one pre-flight an agent has', which is not true of the surface, so the fix is narrower than its own description. Found by the independent reviewer at the RUN-01KXXERR close.

## Steps to Reproduce

In a scratch workspace create sdlc-studio/bugs/BG0001-x.md with Status Open, Severity Low, Points 2 and NO 'Verification depth' line, plus a matching _index.md row. Then: python3 artifact.py close --id BG0001 --dry-run  -> prints 'would close BG0001'. And: python3 transition.py set --id BG0001 --status Fixed --dry-run  -> prints 'blocked ... no parseable Verification depth field'. The two disagree about the same transition.

## Proposed Fix

Route artifact.py close --dry-run through the same gate evaluation transition uses - ideally by calling transition(..., `dry_run`=True) and reporting the GateRefusal blocks, rather than returning a preview before the gates run. Add a regression test asserting the two surfaces agree on a unit that fails a terminal-transition requirement.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
