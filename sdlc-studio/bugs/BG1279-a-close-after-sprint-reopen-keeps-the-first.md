# BG1279: A close after `sprint reopen` keeps the first close's token reading, so the reopened work is missing from the report's cost

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** run eight (RUN-01M6RZQZ): first close bca8b1e6 and second close 2151a7b7 both report 44,550,286 priced; RPT0027 fingerprint 17a047f494e68304
> **Created:** 2026-11-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-07T00:17:07Z

## Summary

RUN-01M6RZQZ was closed, reopened for BG1278 (D0426) and closed again. The second close re-filed RPT0027 with the first close's priced cost, 44,550,286, unchanged, though the reopen added BG1278's builder work, its review and about 25 orchestrator calls at roughly 750k context, about 2M priced. The signed report under-states the run's cost by that amount, and the per-point figure (1.09M) reads lower than it was.

## Steps to Reproduce

Close a run, `sprint reopen` it, do some agent work, close it again, and compare the report's Priced cost row with the meter over the run's whole window.

## Proposed Fix

On a close after a reopen, re-read the meter over the run's full window (open to the new close), or add the reopen span's reading to the first, and say on the report which it did.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: RUN-01M6RZQZ was closed, reopened for BG1278 (D0426) and closed again.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Close a run, `sprint reopen` it, do some agent work, close it again, and compare the report's Priced cost row with the meter over the run's whole window.
- [ ] **AC3** The proposed fix lands, pinned by a test: On a close after a reopen, re-read the meter over the run's full window (open to the new close), or add the reopen span's reading to the first, and say on the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-07 | Claude Opus 5.5 | Filed |
