# BG0795: The sprint report reads a week-old CI cache as current, so DORA's failure rate and restore time read no forge data

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-27T07:29:10Z

## Summary

`sprint_report._ci_runs` reads sdlc-studio/.local/ci-runs.json whenever it exists and writes it only when absent. The file was written 2026-09-18 and never refreshed, so RPT0010 (RUN-01M3CK1K, 2026-09-25 to 26) found no CI run in its window and printed change failure rate and time to restore as NOT MEASURED - no forge run data, while the forge holds every run. The cache is described as 'for this run' but is per clone.

## Steps to Reproduce

ls -la sdlc-studio/.local/ci-runs.json (Sep 18); `sprint_report.py` render --report RPT0010: DORA rows read no forge run data.

## Proposed Fix

Key the cache to the run (or refresh when the run window ends after the cache's newest row), so a report re-derives from the data it was built from and a new run reads the forge; test with a stale cache and a window past it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint_report._ci_runs` reads sdlc-studio/.local/ci-runs.json whenever it exists and writes it only when absent.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: ls -la sdlc-studio/.local/ci-runs.json (Sep 18); `sprint_report.py` render --report RPT0010: DORA rows read no forge run data.
- [ ] **AC3** The proposed fix lands, pinned by a test: Key the cache to the run (or refresh when the run window ends after the cache's newest row), so a report re-derives from the data it was built from and a new...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
