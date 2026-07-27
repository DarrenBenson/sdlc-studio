# CR-0445: Burn down the 19 duplicate Verify selector groups the ratchet baselines

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/stories, .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (scope residue from the D0069 cap); agent; skill v5.0.0

## Summary

US0461 ships a ratchet that refuses NEW duplicate Verify selectors, and baselines the 19 groups already in the corpus - 13 wholly intra-story, the rest crossing stories. The baseline is recorded debt, not a fix: those 19 groups are ACs whose evidence does not discriminate between them, which is the CR0433 defect still live in the artefacts that carry it.

## Impact

Who: anyone reading a Done story's evidence and taking a shared selector as proof of the criterion beside it. What breaks: nothing new, but the existing 19 stay wrong and the ratchet's baseline makes them permanently invisible unless a unit pays them down.

## Acceptance Criteria

- [ ] Each baselined duplicate group is split into discriminating selectors or its reason is recorded, and the baseline shrinks to zero.
- [ ] Four intra-story groups the round-two review found unanswerable by collection are named individually with what makes them so.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (scope residue from the D0069 cap) | Raised |
