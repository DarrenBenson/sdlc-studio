# CR-0467: The one-lane-one-file changelog rule and the [Unreleased] rule contradict each other under parallel delivery

> **Status:** In Progress
> **Decomposed-into:** EP0183
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/../reference-doctrine.md, .claude/skills/sdlc-studio/scripts/changelog.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

Every unit owes a CHANGELOG entry, and parallel lanes cannot all edit CHANGELOG.md, so fragments exist - but the guidance still tells an author to add an [Unreleased] entry, and a lane following it either collides with a sibling or is refused. The two rules need reconciling for the parallel case the skill now recommends.

## Impact

Every unit owes a CHANGELOG entry, and parallel lanes cannot all edit CHANGELOG.md, so fragments exist - but the guidance still tells an author to add an [Unreleased] entry, and a lane following it either collides with a sibling or is refused. The two rules need reconciling for the parallel case the skill now recommends.

## Acceptance Criteria

- [ ] The behaviour in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Raised |
