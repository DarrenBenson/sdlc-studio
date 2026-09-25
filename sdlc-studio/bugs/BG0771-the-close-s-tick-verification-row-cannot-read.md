# BG0771: The close's tick-verification row cannot read the lean criterion shape

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T12:01:16Z

## Summary

`sprint_report._ticked_criteria` reads a criterion as done only from a '- [x]' tick or a 'Verified: yes' line under a '### ACn' heading. The lean story shape every Sprint 4 unit uses is a '- **ACn:**' bullet with '- **Verify:**' and '- **Verified:** yes' sub-bullets, so at RUN-01M3BK9Y's close the row examined none of 35 units and refused 'no ticked criteria found'. Sprint 3 passed only because BG0742 carried '[x]' ticks.

## Steps to Reproduce

1. sprint.py close --retro RETRO0124 --dry-run on RUN-01M3BK9Y (2026-09-25). 2. The checklist refuses tick-verification: 'none of the 35 unit(s) carries a criterion this row can read'. 3. Every batch unit carries '- **Verified:** yes' under '- **ACn:**' bullets.

## Proposed Fix

Treat a '- **ACn:**' bullet as the heading for the Verified line that follows it in `_ticked_criteria`, with a fixture in the lean shape.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint_report._ticked_criteria` reads a criterion as done only from a '- [x]' tick or a 'Verified: yes' line under a '### ACn' heading.
- [ ] **AC2** The proposed fix lands, pinned by a test: Treat a '- **ACn:**' bullet as the heading for the Verified line that follows it in `_ticked_criteria`, with a fixture in the lean shape.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
