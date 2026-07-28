# BG0373: The review-currency carve-out repaired in BG0336 remains story-shaped, so a bug or change request takes a different path

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

BG0336 fixed the direction-blindness of the review-currency close-bookkeeping carve-out. The repaired path still reasons in stories: a bug or change request in the same diff is judged by the pre-existing route, so the class of hand-edited status change the bug was filed about is still reachable through a non-story unit.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review of BG0336's repair. The fix is correct for the type it covers; the coverage is the defect.

## Proposed Fix

Apply the carve-out rule by unit rather than by story, so every delivery type takes one path, and assert the property across types rather than for a story fixture.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: none of its prose fields carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
