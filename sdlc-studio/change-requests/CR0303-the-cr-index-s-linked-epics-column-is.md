# CR-0303: The CR index's Linked Epics column is dead: '--' on every row while at least seven CR files carry a Decomposed-into epic link

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/change-requests/_index.md, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/refine.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

change-requests/_index.md has a Linked Epics column whose entire purpose is CR->epic traceability, and every live row reads '--' - while CR0271/CR0272/CR0274-CR0278 each carry '> **Decomposed-into:** EPxxxx' in-file. The refine/decompose path writes the file header but never the index column, and reconcile detect reports 0 drift because it does not census this column - despite the 'index is derived, reconcile syncs it' doctrine, and archives showing the column was historically populated. Panel confirmed 3x but noted 'no queryable view' is overstated (`children_of`/refine show read the file links), so severity is low: sync the column or drop it from the template so the index stops asserting no CR ever spawned an epic.

## Impact

change-requests/_index.md has a Linked Epics column whose entire purpose is CR->epic traceability, and every live row reads '--' - while CR0271/CR0272/CR0274-CR0278 each carry '> **Decomposed-into:** EPxxxx' in-file.

## Acceptance Criteria

- [ ] reconcile syncs the Linked Epics column from Decomposed-into headers (the seven existing links appear, future drift detected), or the column is removed from the template and live index
- [ ] refine/decompose keeps the chosen home consistent on future decompositions

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
