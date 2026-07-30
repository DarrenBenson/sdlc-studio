# BG0377: Four of the five Caller declarations added at review resolve only on the documentation filename, not on the caller they name

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/stories/US0508-a-lane-refuses-to-start-on-a-unit.md
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent re-review of 343da768, run wf_b62b2ed2); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_b62b2ed2

## Summary

The repair added Caller declarations to five stories to close the inert-verb finding. Four of them name an internal call chain that resolves to nothing, and pass the resolver only because a documentation filename was appended to the same line. The declaration therefore records a caller that does not exist while satisfying the check, which is the theatre the caller check was repaired to stop two findings earlier in the same review. Seventeen of the batch's twenty-three stories still report caller-unnamed, so the repair's claim that the count reached zero is false.

## Steps to Reproduce

Independent re-review of 343da768. Resolve each added Caller declaration in turn: the named call chain resolves to nothing for four of five; removing the trailing documentation filename makes them fail. Separately, the caller-finding library call over the batch's stories returns 17 findings, and over the six lane units returns 1 (US0513).

## Proposed Fix

Declare the caller that actually consumes the mechanism, and where none exists yet say so explicitly and name the follow-up - which is the path US0513 already provides. Correct the claim in the retro and in the review record rather than leaving a false count on the file.

## Acceptance Criteria

### AC1: a caller named as a symbol resolves without an incidental path token

- **Given** a Caller declaration naming a real function in a tracked source file and no path
- **When** the declaration is resolved
- **Then** it resolves on the symbol, while prose such as `unknown` or `the main loop` still does not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerResolverAtScaleTests
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (independent re-review of 343da768, run wf_b62b2ed2) | Filed |
| 2026-07-28 | Claude Opus 5 | Fixed: the declarations were TRUE - the resolver could not see a symbol caller after the path-shaped repair. `tree_index` now indexes defined symbols and all five resolve on the caller itself, not on an appended documentation filename. |
