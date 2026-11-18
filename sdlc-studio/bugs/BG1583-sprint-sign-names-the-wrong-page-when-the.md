# BG1583: sprint sign names the wrong page when the later run has also closed, and three of US1290's guards have no test

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** sdlc-studio/reviews/verdicts/US1290/1d42d95f5aae-72f7cc40.txt and b9e0f15856ad-b543e9a9.txt
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T03:20:36Z

## Summary

The QA seat's two rounds on US1290 (run sixteen, APPROVE in round 2) carried two non-blocking findings: when a run waits and a later run has closed too, sign's refusal names the later run's page instead of the one asked for; and three guards US1290 added are exercised by no test.

## Steps to Reproduce

See the round-1 and round-2 verdicts for US1290 for the probes and the three guards.

## Proposed Fix

Name the requested report in the refusal, and pin each guard beside a positive control.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The QA seat's two rounds on US1290 (run sixteen, APPROVE in round 2) carried two non-blocking findings: when a run waits and a later run has closed too, sign's...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: See the round-1 and round-2 verdicts for US1290 for the probes and the three guards.
- [ ] **AC3** The proposed fix lands, pinned by a test: Name the requested report in the refusal, and pin each guard beside a positive control.

## Impact

A misleading refusal, and guards that could be removed with the suite still green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
