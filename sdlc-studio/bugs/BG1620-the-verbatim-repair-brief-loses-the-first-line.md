# BG1620: The verbatim repair brief loses the first-line indentation of a REJECT finding written over several lines, and its newest-landing choice and superseded filter have no test

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_brief_repair_scope.py, changelog.d/BG1620.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** run eighteen, 2026-11-19: sdlc-studio/reviews/verdicts/US1195/793885098a21-a2a6a6dc.txt and sdlc-studio/reviews/verdicts/US1195/16ba58a543e2-2a24e49b.txt
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T14:55:16Z

## Summary

Non-blocking findings from both seats' reviews of the repair brief (run eighteen): a blocking finding that spans several lines loses its first line's indentation in the repair brief, and the test cannot catch it; the choice of the newest landing and the filter of superseded verdicts are reached by no test.

## Steps to Reproduce

Record a REJECT whose blocking finding spans two indented lines, then run `sprint.py lane brief --units <id>`: the first line of the quoted finding is unindented.

## Proposed Fix

Quote each finding's lines unchanged and pin it with a multi-line fixture; test the newest-landing choice and the superseded filter.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Non-blocking findings from both seats' reviews of the repair brief (run eighteen): a blocking finding that spans several lines loses its first line's...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Record a REJECT whose blocking finding spans two indented lines, then run `sprint.py lane brief --units <id>`: the first line of the quoted finding is...
- [ ] **AC3** The proposed fix lands, pinned by a test: Quote each finding's lines unchanged and pin it with a multi-line fixture; test the newest-landing choice and the superseded filter.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
