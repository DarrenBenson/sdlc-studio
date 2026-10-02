# BG0908: Close steps hand over their status and prose lines as known issues

> **Status:** In Progress
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_gap_lines.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** BG0894 QA review (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T14:03:42Z

## Summary

`close_known_issues_from` turns every detail line of a failed close step into a known issue (sprint.py:7633), so review-coverage hands over its '1/2 unit(s) covered' status line and its certification prose (sprint.py:5289, 5295) as two extra issues beside the real gap, retro-validate its explanatory header (sprint.py:4683), and the gate's unattributed path its whole output plus prose (sprint.py:5108). BG0894 fixed the same shape in retro-extract only, and its extract-failed branch (rc not 0) is unpinned.

## Steps to Reproduce

1. A close with one unreviewed unit. 2. The page lists 3 known issues for 1 review-coverage gap.

## Proposed Fix

Have each step hand over only its failures, as BG0894 did for retro-extract, and pin retro-extract's extract-failed branch.

## Acceptance Criteria

- [ ] **AC1** Given a close whose only gap is one unreviewed unit, when the page is filed, then its known issues hold exactly one review-coverage gap naming that unit and no status or prose line. Fails on: the current code hands over three
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_gap_lines.py::CloseGapLinesTests::test_review_coverage_hands_over_only_its_gap
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
