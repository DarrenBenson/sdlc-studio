# BG0716: PREPARE mints a new report id on every re-file, so a run that prepares twice has two reports of record

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_file_the_report` calls `file_report`, which allocates a fresh RPT id through `next_id` on every call. PREPARE is rerunnable by contract - US0832 AC4 requires it to RE-DERIVE rather than reuse the filed page - so a run that prepares five times leaves RPT0001..RPT0005, each a complete report of record for the same run and only the last one true. The report index's row writer already assumes id stability: it REPLACES a report's own row on a re-file, which is the shape the filer should have had. Found during the close of the run that shipped the report of record.

## Steps to Reproduce

1. Open a run and work its batch to a state PREPARE accepts. 2. Run `sprint close --retro RETROxxxx --goal-verdict achieved` - it files RPT0001 and names it in the run record. 3. Change anything the page derives from, then run the same close again. 4. Read `sdlc-studio/reports/`: RPT0002 is filed beside RPT0001, both complete reports of record for one run, and the index carries a row for each. Observed on RUN-01M2SPNS.

## Proposed Fix

In `file_report` (or its caller `_file_the_report`), take the report id from the run record when the run already names one and allocate through `next_id` only when it does not. The re-derived page then overwrites the run's single report, the index row writer's existing replace-on-re-file behaviour becomes correct rather than coincidental, and US0832 AC4's requirement to re-derive is unaffected - what changes is where the page is written, not whether it is rebuilt. Add a criterion that prepares twice and asserts one report file and one index row.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_file_the_report` calls `file_report`, which allocates a fresh RPT id through `next_id` on every call.
- [ ] **AC2** The proposed fix lands, pinned by a test: In `file_report` (or its caller `_file_the_report`), take the report id from the run record when the run already names one and allocate through `next_id` only...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-18 | sdlc-studio | Filed |
