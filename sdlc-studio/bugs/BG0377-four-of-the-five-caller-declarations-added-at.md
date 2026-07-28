# BG0377: Four of the five Caller declarations added at review resolve only on the documentation filename, not on the caller they name

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/stories/US0508-a-lane-refuses-to-start-on-a-unit.md
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent re-review of 343da768, run wf_b62b2ed2); agent; skill v5.0.0

## Summary

The repair added Caller declarations to five stories to close the inert-verb finding. Four of them name an internal call chain that resolves to nothing, and pass the resolver only because a documentation filename was appended to the same line. The declaration therefore records a caller that does not exist while satisfying the check, which is the theatre the caller check was repaired to stop two findings earlier in the same review. Seventeen of the batch's twenty-three stories still report caller-unnamed, so the repair's claim that the count reached zero is false.

## Steps to Reproduce

Independent re-review of 343da768. Resolve each added Caller declaration in turn: the named call chain resolves to nothing for four of five; removing the trailing documentation filename makes them fail. Separately, the caller-finding library call over the batch's stories returns 17 findings, and over the six lane units returns 1 (US0513).

## Proposed Fix

Declare the caller that actually consumes the mechanism, and where none exists yet say so explicitly and name the follow-up - which is the path US0513 already provides. Correct the claim in the retro and in the review record rather than leaving a false count on the file.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: `steps` carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (independent re-review of 343da768, run wf_b62b2ed2) | Filed |
