# CR-0265: RFC0038 U1: Points (modified Fibonacci) become the one size vocabulary, replacing Effort S/M/L

> **Status:** Complete
> **Size:** M
> **Priority:** P1
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/templates/core/cr.md, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Delivered-by:** claude-opus-4-8

## Summary

RFC0038 proved by blind experiment that a relative Fibonacci estimate predicts cost (r = 0.68 pooled, 0.78 on units of 8 or below) where every computed metric failed (`max_cognitive` scored 0.03). Effort S/M/L scored 0.35 - better than the machine, worse than points, and a second size vocabulary nobody needs.

This unit introduces the field and retires its predecessor. Points: one of 1, 2, 3, 5, 8, 13, 20 (modified Fibonacci). The gaps widen deliberately, because uncertainty grows with size: it is much harder to argue a story is a 7 rather than an 8 than to choose between a 5 and an 8. That is the whole reason the scale exists, and it is the property a linear scale destroyed.

Estimated at 5 points by the new scale, before the work: several files, a clear approach, a migration to think about.

## Impact

Every artefact filed from now on. It replaces a three-level ordinal (S/M/L) that scored 0.35 with a seven-level relative scale that scored 0.68, and it removes one of the five overlapping size signals this project had accumulated.

**Effort:** M

## Acceptance Criteria

- [ ] A bug, CR and story carry `Points:` on the modified Fibonacci scale (1, 2, 3, 5, 8, 13, 20). A value off the scale is refused - the scale IS the estimate, and a 7 is a false precision the scale exists to prevent.
- [ ] The filer and artifact.py both demand Points from one shared definition, so the two creation paths cannot disagree about what a sized artefact is.
- [ ] `Effort` S/M/L is removed from the templates, the filer and the parser. Nothing reads two size vocabularies.
- [ ] The open backlog is re-estimated in points rather than mechanically mapped from S/M/L: a map would manufacture estimates nobody made, and the whole finding is that a real relative estimate is what carries the signal.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
