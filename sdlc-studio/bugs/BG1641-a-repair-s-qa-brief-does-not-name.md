# BG1641: A repair's QA brief does not name the reviewer whose REJECT it answers, so a fresh reviewer's round two is refused at record

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T00:35:57Z

## Summary

critic.py record refuses a round-two verdict from anyone but the reviewer who rejected round one (critic.py:1986-1990). The QA brief lane land writes for a repaired unit (lib/lanes.py) quotes the REJECT but never says the round must go back to that reviewer, and lane accept only finds out after the review has run. In RUN-01M7TTK3 the orchestrator briefed fresh qa reviewers for BG1543, BG1525, BG1180 and BG1553 from those briefs; all four APPROVEs were refused at record and the round-one reviewers had to be resumed and briefed again, at the cost of two complete reviews.

## Steps to Reproduce

Record a REJECT on a unit, land its repair with sprint.py lane land, read the QA brief it writes (sdlc-studio/.local/briefs/<ID>-qa.txt): no line names the reviewer round two must come from. Record an APPROVE from another reviewer with lane accept: refused, 're-checks the fixes to <reviewer>'s REJECT'.

## Proposed Fix

When the unit has an unanswered REJECT, have the QA brief open with the reviewer who must judge round two and the instruction to resume that reviewer rather than spawn a new one, and have lane land print the same line beside the brief path.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: critic.py record refuses a round-two verdict from anyone but the reviewer who rejected round one (critic.py:1986-1990).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Record a REJECT on a unit, land its repair with sprint.py lane land, read the QA brief it writes (sdlc-studio/.local/briefs/<ID>-qa.txt): no line names the...
- [ ] **AC3** The proposed fix lands, pinned by a test: When the unit has an unanswered REJECT, have the QA brief open with the reviewer who must judge round two and the instruction to resume that reviewer rather...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
