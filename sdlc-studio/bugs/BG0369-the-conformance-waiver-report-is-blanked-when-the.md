# BG0369: The conformance waiver report is blanked when the diff contains no stories, hiding a waived unit rather than reporting it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0525 has the conformance lane read recorded waivers and report a waived unit as waived, naming the waiver. The report is emitted from a story-scoped path, so a diff containing no story emits nothing at all - a waiver covering a bug or a change request is silently in force with no line saying so, which is the outcome the story exists to prevent.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review, alongside BG0336's related over-narrowing to stories. Run the lane over a diff of bugs only and the waiver section is absent rather than empty-with-reason.

## Proposed Fix

Scope the waiver report to the units in the diff whatever their type, and emit an explicit none-in-force line when there are no waivers, so absence of output is never the same as absence of waivers.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: none of its prose fields carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
