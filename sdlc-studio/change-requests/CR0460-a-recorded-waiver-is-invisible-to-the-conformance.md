# CR-0460: A recorded waiver is invisible to the conformance lane, so waived debt blocks every clean-tree close

> **Status:** Complete
> **Decomposed-into:** EP0180
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/decisions.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ close, second consecutive occurrence); agent; skill v5.0.0

## Summary

D0074 waives the pre-two-role critic debt on 25 historical units, recorded through the sanctioned decisions waive path. conformance.py never reads waivers at all, so the lane reports those units as non-conformant on every run. It only appears to pass when the gate has a diff to scope to; on a CLEAN tree it judges the whole workspace and the waived debt blocks the close. That is exactly the state a close runs in, so the waiver is invisible precisely when it is needed.

## Impact

Who: any project that waives a rule for recorded, reasoned debt - the sanctioned escape hatch the gate itself recommends in its own remedy text. What breaks: the waiver does nothing, so the only way past the lane is to raise `adopt_after`, which hides the debt instead of pricing it. Two consecutive sprint closes have been blocked by this and both times the operator had to rule on inherited debt that was already recorded as accepted.

## Acceptance Criteria

- [ ] conformance reads the recorded waivers and reports a waived unit as waived rather than non-conformant, naming the decision that waived it.
- [ ] A waiver that names no reason, or names a rule that does not exist, is refused at record time rather than silently doing nothing.
- [ ] The gate's remedy text and the behaviour agree: if it recommends a waiver, a waiver must clear the lane.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ close, second consecutive occurrence) | Raised |
