# BG0396: cmd_seams silently drops unresolvable ids and re-implements the worklist reader the planner refuses on

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

`refine seams --units US9999` prints the all-clear at exit 0. `sprint._worklist_units` uses `ID_SEARCH_RE`, dedupes and RAISES on ids not on disk because 'a silent skip would ship a smaller tranche than approved'; `cmd_seams` re-implements the reader with none of that, so a worklist with `US0541 (3 pts)` resolves to nothing and reports no seams.

## Steps to Reproduce

refine.py seams --units 'US9999,US9998' -> 'nothing to own', exit 0.

## Proposed Fix

Reuse `_worklist_units` and report unresolved ids.

## Acceptance Criteria

### AC1: an unresolvable id is refused, not skipped

- **Given** `refine seams --units US9999,US9998`, neither of which is on disk
- **When** the seam map runs
- **Then** it refuses with exit 2 naming both ids, rather than printing the all-clear over units nobody looked at
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeamOwnershipDefectsTests::test_an_unresolvable_id_is_refused_not_skipped
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
