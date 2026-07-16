# CR-0268: RFC0038 U4: an epic carries a T-shirt size, not story points - and its point total is DERIVED, not estimated

> **Status:** Complete
> **Size:** S
> **Priority:** P2
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/templates/core/epic.md, .claude/skills/sdlc-studio/scripts/reconcile.py
> **Verification depth:** functional - reconcile derives the epic roll-up from story points, attacked through the public CLI: a 3+5+2 epic recomputes to 10, bumping a story to 8 recomputes to 15, the DERIVED note survives, and a Size-only epic never drifts and its T-shirt is never summed.
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Delivered-by:** claude-opus-4-8

## Summary

The epic template asks for `**Story Points:**` on the epic itself. That is asking someone to point an epic, and the clue is in the name: STORY points belong on stories. Operator experience, and standard practice: epics are T-shirt sized (S/M/L/XL), stories are pointed.

The template also conflates two different things under one field:

- THE ESTIMATE, made BEFORE decomposition, when the stories are not yet known. That is necessarily coarse, and a T-shirt size is coarse ON PURPOSE - it says "roughly this big" without pretending to a precision nobody has.
- THE ROLL-UP, the sum of the epic stories points. That only exists AFTER decomposition, and it is DERIVED, never estimated.

Asking for story points on an epic demands the second before the first is possible. It is the same false-precision error the Fibonacci scale exists to prevent (RFC0038: a 7 is refused because the gaps ARE the estimate), one level up the hierarchy.

The distinction matters beyond tidiness. A derived roll-up can be RECOMPUTED and reconciled against the stories, so it can never silently drift. An estimated one cannot be checked against anything, and a number nobody can check is the false authority this project keeps hunting.

## Impact

Every epic. Today an epic carries a number that is neither an honest coarse estimate nor a checkable roll-up, and nothing reconciles it against the stories beneath it.

**Points:** 2

## Acceptance Criteria

- [ ] An epic carries a T-shirt `Size:` (S/M/L/XL) as its own coarse estimate, made before decomposition. It is never expressed in story points.
- [ ] An epic point total is DERIVED from the points of its stories, clearly labelled as derived, and recomputed by reconcile so it cannot drift from the stories beneath it.
- [ ] Story points remain on stories, bugs and CRs - the units that enter a sprint - on the modified Fibonacci scale, as RFC0038 established.
- [ ] Nothing asks a human to estimate an epic in story points, and nothing sums a T-shirt size into a velocity figure.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
