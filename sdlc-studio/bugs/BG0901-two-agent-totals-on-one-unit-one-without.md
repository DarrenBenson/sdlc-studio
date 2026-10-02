# BG0901: Two agent totals on one unit, one without minutes, fall back to the span unlabelled

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_partial_agent_minutes.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** US0980 QA review round 1 (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T12:59:01Z

## Summary

`sprint_report` reads a unit's agent minutes only when every agent total tagged to it carries minutes (the timed == agents rule at `sprint_report.py`:3302, BG0797). A builder total with 40 minutes plus a second total with none makes the unit read its 7-minute span unlabelled while its tokens read 300,000 agent tokens, so the precedence US0980 states (agent minutes over the span) holds only when every total carries minutes.

## Steps to Reproduce

1. lane return US0101 --tokens 250000 --minutes 40 (span 7). 2. A second total for US0101 with --tokens 50000 and no minutes. 3. The page reads 7.0 unlabelled.

## Proposed Fix

Sum the agent minutes that were supplied, labelled as agent minutes over the agents that supplied them, and fall back to the span only when no agent supplied minutes.

## Acceptance Criteria

- [ ] **AC1** Given unit X with a 7-minute span, a 40-minute agent total and a second agent total with no minutes, when the page is derived, then X's minutes read 40 labelled agent minutes, never the 7-minute span. Fails on: the current code reads 7.0 unlabelled
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_partial_agent_minutes.py::PartialAgentMinutesTests::test_supplied_agent_minutes_win_when_one_agent_gave_none

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
