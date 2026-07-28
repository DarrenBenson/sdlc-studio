# CR-0465: reconcile's sweep detectors re-read the whole corpus per unit: 733,271 file opens for one run

> **Status:** In Progress
> **Decomposed-into:** EP0181
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

Measured by a lane: the sweep detectors open the artefact corpus once per unit rather than once per run, for 733,271 opens and about 25 seconds. reconcile runs in the gate, so this is per-commit cost of the same kind as the constitution lane, and it is invisible because nothing attributes gate seconds to a lane.

## Impact

Measured by a lane: the sweep detectors open the artefact corpus once per unit rather than once per run, for 733,271 opens and about 25 seconds. reconcile runs in the gate, so this is per-commit cost of the same kind as the constitution lane, and it is invisible because nothing attributes gate seconds to a lane.

## Acceptance Criteria

- [ ] The behaviour in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Raised |
