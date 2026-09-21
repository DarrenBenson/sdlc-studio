# BG0730: a stop-ship ruling is never re-derived against its finding's status, so a ruling on a Fixed finding blocks every close permanently

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0463 claim 23, still true and the most consequential survivor. `retro.carried_issues` parses the retro's table and never reads the named artefact's current status; `sprint_report.py:2144` collects every row whose ruling is `STOP_SHIP`; the checklist then returns non-zero while any `stop_ship` row stands. Nothing joins the ruling to the finding. So once a finding is ruled stop-ship it blocks every subsequent close FOREVER, including after it has been Fixed - the ruling outlives the thing it ruled on, and the only escape is editing a retro by hand.

## Steps to Reproduce

1. Rule a finding stop-ship in a retro's carried table. 2. Fix that finding and transition it to Fixed. 3. Run the close checklist on a later run. 4. The stop-ship row still stands and the checklist still refuses.

## Proposed Fix

Join each carried stop-ship row to its artefact's current status when the checklist is derived. A finding that has reached a terminal status is discharged - or, if the distinction matters, reported as `ruling outlived its finding` so a reader can see what happened - rather than counted as an unconditional blocker. Pin both: a stop-ship on an open finding still blocks, and the same row on a Fixed finding does not.

## Acceptance Criteria

### AC1: a stop-ship ruling on a finding that has reached a terminal status no longer blocks the close

- **Given** a retro carrying a stop-ship ruling on a finding that has since been Fixed, and a second ruling on a finding still Open as the control
- **When** the close checklist is derived
- **Then** the Open one still blocks and the Fixed one is discharged - or reported as a ruling that outlived its finding - so a ruling cannot outlive the thing it ruled on
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, collect every stop-ship row without joining it to its artefact's status, which is the shipped behaviour: a ruling then blocks every subsequent close forever and the only escape is editing a retro by hand
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::StopShipDischargeTests::test_a_ruling_on_a_fixed_finding_is_discharged_and_an_open_one_still_blocks

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
