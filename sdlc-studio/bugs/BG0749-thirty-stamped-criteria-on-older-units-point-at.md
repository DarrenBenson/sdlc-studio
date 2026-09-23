# BG0749: Thirty stamped criteria on older units point at tests this sprint made skipped stubs

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

D0259 records the criteria superseded by US0876, US0868 and D0258: US0351, US0435, US0600, BG0517, BG0635, US0834, US0282 AC1, US0283 AC1, US0592, US0297 AC3, BG0262 AC1, US0336 and US0338. `verify_ac` reads them red (all skipped), and the release gate's verify lane would flag them. Retire the Verify lines and delete the stub tests together, before any release.

## Steps to Reproduce

Run `verify_ac.py run --dry-run --ids US0592,US0297` on main: the named criteria read FAIL because every selected test is skipped.

## Proposed Fix

In one unit: rewrite each superseded criterion's Verify line to name the unit that superseded it, then delete the stub tests the stamps-staged lane now protects.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: D0259 records the criteria superseded by US0876, US0868 and D0258: US0351, US0435, US0600, BG0517, BG0635, US0834, US0282 AC1, US0283 AC1, US0592, US0297 AC3...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run `verify_ac.py run --dry-run --ids US0592,US0297` on main: the named criteria read FAIL because every selected test is skipped.
- [ ] **AC3** The proposed fix lands, pinned by a test: In one unit: rewrite each superseded criterion's Verify line to name the unit that superseded it, then delete the stub tests the stamps-staged lane now...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Filed |
