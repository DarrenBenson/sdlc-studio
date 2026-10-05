# BG0946: reports/_index.md Last Updated is not restamped when a report is filed

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Created:** 2026-10-05
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-05T15:44:22Z

## Summary

`sdlc-studio/reports/_index.md` says `**Last Updated:** 2026-09-18` while listing RPT0019, generated 2026-10-05. `reconcile detect` reports 0 drift, so the stale-index-stamp check does not cover the report index either.

## Steps to Reproduce

1. Read the `**Last Updated:**` line of sdlc-studio/reports/_index.md (2026-09-18). 2. Read RPT0019's row and `generated_at` in reports/RPT0019.json (2026-10-05). 3. Run reconcile.py detect: 0 drift.

## Proposed Fix

Restamp the report index when `sprint close` files a report, and extend the stale-index-stamp check to the report index.

## Acceptance Criteria

- [ ] **AC1** Filing a report restamps `reports/_index.md` Last Updated to the filing date
- [ ] **AC2** `reconcile detect` reports stale-index-stamp for a report index whose header is older than its newest row

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-05 | Claude Opus 5.5 | Filed |
