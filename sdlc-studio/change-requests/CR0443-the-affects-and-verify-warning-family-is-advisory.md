# CR-0443: The Affects and Verify warning family is advisory at 398 instances, so a new one is invisible

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (dogfooding friction, pre-sprint check RUN-01KYHVWK); agent; skill v5.0.0

## Summary

validate.py reports 0 errors and 398 warnings, all three kinds concerning the same thing - whether a unit's declared footprint and its acceptance criteria agree with the repo. 191 affects-undeclared (a Verify line targets a file the Affects omits), 139 pseudo-verify (a CR or RFC criterion carries a command-shaped Verify that nothing executes), 68 affects-unresolvable (a declared path is not on disk). None blocks. At that volume a new instance cannot be seen, so the check reports a defect without preventing one.

## Impact

Who: anyone relying on validate to tell them a unit is well-formed, and every consuming project inheriting the same advisory posture. What breaks: the signal exists and is ignored, which is worse than not computing it - the 191 affects-undeclared warnings are precisely the defect that will under-read every unit of the sprint starting now, and they were being reported the whole time. A warning nobody can act on trains a reader to skip the output, taking the errors with it.

## Acceptance Criteria

- [ ] A ratchet holds the count: the current instances are recorded as a baseline and a NEW instance fails, so the backlog can be paid down without blocking work on artefacts nobody is touching.
- [ ] The baseline is derived by counting the corpus rather than stored as a hand-written number, so it cannot drift from what the checker actually finds.
- [ ] Each warning kind reports its own count and baseline separately, so a new affects-undeclared is not hidden by a pseudo-verify that was paid off in the same commit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (dogfooding friction, pre-sprint check RUN-01KYHVWK) | Raised |
