# BG1696: sprint drive's headless review passes no effort, while the sprint report says the reviewer ran at the plan's stamp

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_drive_review_effort.py, changelog.d/BG1696.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** lib/drive.py:499 calls lanes.headless_command with no effort; sdlc-studio/reviews/verdicts/BG1539/c6e75ea15079-490ff16f.txt records it [pre-existing].
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T21:16:36Z

## Summary

sprint drive runs each unit's review step headless through `lanes.headless_command(w.harness`, brief, w.model, w.root) (lib/drive.py:499) with no effort argument, so the reviewer runs at the harness default. The sprint report's `effort_reviewer` row still reports the plan's stamped effort as the effort a drive-run reviewer was dispatched at, so a reader is told a reviewer effort that was never applied. Run twenty-one's BG1539 fixed the same gap for the builder only. Confirmed by the qa seat in BG1539's review as already true at the run base.

## Steps to Reproduce

1. Plan a run with an effort stamp (for example high) and run it with sprint drive on a headless harness. 2. Read the headless review command drive runs (no effort flag). 3. Run sprint report: `effort_reviewer` reads the plan's stamp as dispatched.

## Proposed Fix

Pass the stamped effort to `headless_command` in `drive._review` the way lane run now does for the builder (`effort_carried)`, and report a reviewer effort the harness could not carry as not applied, as BG1539 does for the builder.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: sprint drive runs each unit's review step headless through `lanes.headless_command(w.harness`, brief, w.model, w.root) (lib/drive.py:499) with no effort...
- [ ] **AC2** The proposed fix lands, pinned by a test: Pass the stamped effort to `headless_command` in `drive._review` the way lane run now does for the builder (`effort_carried)`, and report a reviewer effort the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
