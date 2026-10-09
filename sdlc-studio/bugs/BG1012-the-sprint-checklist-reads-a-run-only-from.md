# BG1012: The sprint checklist reads a run only from .local, so in any other clone a signed run's rows read 'no run record could be read'

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_checklist_reads_tracked_record.py, changelog.d/BG1012.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** Live read at d327d5d0: the RETRO0133 checklist in this clone; sprint_report.py `_run_record` against `_run_state_for`.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T09:02:38Z

## Summary

`_run_record` (`sprint_report.py`:101-128) looks for the run only in `.local/run-state.json` and its archive, never in the committed `sdlc-studio/reports/runs/<RUN>.json` that sign (and, since BG0993, close) files. Reproduced at d327d5d0 in this repository: `sprint_report.py checklist --id RETRO0133` reports `no run record could be read, so whether anything was blocked is unknown` and several rows `not measured`, while `reports/runs/RUN-01M45FV6.json` is committed; rows then fall to waivers of any age (BG1008). `_run_state_for` already falls back to the tracked record. BG0989 and BG0993's class: a record kept in `.local` is not a record. Found by the G5 panel review of CR0614 (D0355).

## Steps to Reproduce

In a clone without the closing machine's `.local`, `sprint_report.py checklist --id <retro of a signed run>` -> 'no run record could be read'.

## Proposed Fix

Resolve the run through `_run_state_for` (live, then tracked, then archive), as `check` does, so the checklist reads the committed record in every clone.

## Acceptance Criteria

- [ ] **AC1** `sprint_report.py checklist --id <retro>` in a clean clone holding the run's committed record reads that record, so no row says no run record could be read
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_reads_tracked_record.py::ChecklistTrackedRecordTests::test_a_clean_clone_reads_the_committed_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
