# BG1551: EP0246 stands at Done with all four stories Superseded, and reconcile detect reports no drift on a terminal epic

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, sdlc-studio/epics/EP0246-the-declared-python-floor-is-a-gate-not.md, sdlc-studio/change-requests/CR0561-the-declared-python-3-10-floor-is-stated.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, cross lens, survived 3 of 3 refute votes; observed at sdlc-studio/epics/EP0246-the-declared-python-floor-is-a-gate-not.md Status line and Story Breakdown; sdlc-studio/change-requests/CR0561 Status and Revision History; .claude/skills/sdlc-studio/scripts/reconcile.py:1095-1106 (epic_derived_status)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:22Z

## Summary

reconcile.py holds a rule, `epic_derived_status`, that an epic whose every child was ruled out and not built derives Superseded, so it does not claim a delivery nobody made. EP0246 is Done although US0811 to US0814 are all Superseded by US0908, a CI step under another epic, and its three epic-level criteria describing a refusing gate lane are unticked. Its parent CR0561 is Complete, yet its revision history ends on the 2026-09-21 row that returned it to Proposed, with no row recording the completion. The rule is applied only when a non-terminal epic is closed: the epic drift lanes skip any epic already at a terminal status, so reconcile detect ends with zero drift items. EP0246 is the only Done epic in the corpus with no delivered child. A request therefore reads as delivered when it was replaced by something narrower, and nothing would catch the next one.

## Steps to Reproduce

1. Read sdlc-studio/epics/EP0246-the-declared-python-floor-is-a-gate-not.md. Status is Done and the three epic-level criteria are unticked.
2. Read the status of each story in its breakdown, US0811 to US0814. All four read Superseded, by US0908.
3. Read sdlc-studio/change-requests/CR0561. Status is Complete and the last revision history row is dated 2026-09-21 and returns it to Proposed.
4. Run reconcile.py with the detect verb at the repository root.
5. Observed: the run ends with zero drift items across all scopes.
6. Expected: a drift item naming EP0246 as Done where its children derive Superseded.
7. Positive control: a fixture epic at Draft whose children are all Superseded is reported by the existing stale status lane.

## Proposed Fix

Extend the epic status drift lane in reconcile.py so a terminal epic is also compared with `epic_derived_status` over its declared children, and report a drift item when a Done epic has no Done child, without rewriting it unasked since the status may record a ruling. Add fixture tests in `test_reconcile.py` for a Done epic over all-Superseded children, with a Done epic over a delivered child as the control. Then correct the record: move EP0246 to Superseded naming US0908, or record the decision that keeps it Done, and add the missing completion row to CR0561's revision history saying what delivered it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: reconcile.py holds a rule, `epic_derived_status`, that an epic whose every child was ruled out and not built derives Superseded, so it does not claim a...
- [ ] **AC2** The proposed fix lands, pinned by a test: Extend the epic status drift lane in reconcile.py so a terminal epic is also compared with `epic_derived_status` over its declared children, and report a drift...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
