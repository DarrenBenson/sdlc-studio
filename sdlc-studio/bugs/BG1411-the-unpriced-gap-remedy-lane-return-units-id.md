# BG1411: The unpriced-gap remedy 'lane return --units <id> --agent A' cannot work after the close

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py, .claude/skills/sdlc-studio/scripts/tests/test_unpriced_remedy_after_close.py, changelog.d/BG1411.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: review land, BG1330
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:13:04Z

## Summary

The remedy printed at sprint.py:9879 and `sprint_report.py`:4191 cannot be run once the run is closed.

## Steps to Reproduce

Close with an unpriced unit and run the printed command.

## Proposed Fix

Name the post-close command.

## Acceptance Criteria

- [ ] **AC1** Given a closed run with unpriced units, when the page prints the remedy, then it names a command that works after the close. Fails on: the unusable remedy.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_unpriced_remedy_after_close.py::UnpricedRemedyAfterCloseTests

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. A remedy that cannot run after the close.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
