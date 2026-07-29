# BG0389: Preserves is honoured anywhere in a unit's document, not in a criterion as its docstring states

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`_SEAM_RE` scans the whole file under `re.M`, so a `- **Preserves:**` line under `## User Story` clears the seam. The docstring says 'at least one of the two states, IN A CRITERION, what it must not regress'; `critic.caller_declarations` walks `_ac_blocks_with_bodies` and refuses the same shape.

## Steps to Reproduce

Put the Preserves line above the Acceptance Criteria heading; the seam reports owned.

## Proposed Fix

Walk the AC blocks, as the sibling does.

## Acceptance Criteria

### AC1: a Preserves outside a criterion does not own a seam

- **Given** a `- **Preserves:**` line under `## User Story` rather than in a criterion
- **When** the seam map runs
- **Then** the seam is still reported unowned, which is what the field's own contract has always said
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeamOwnershipDefectsTests::test_a_preserves_outside_a_criterion_does_not_own_a_seam
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
