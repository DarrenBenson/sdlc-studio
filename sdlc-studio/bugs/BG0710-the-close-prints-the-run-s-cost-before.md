# BG0710: the close prints the run's cost before the step that captures it, so every close reports the sprint as not attributable

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RUN-01M2JA6J close, 2026-09-16: close summary COST block against the velocity row recorded minutes later (6,459,675 tokens, 62,715/pt); sprint.py:6842-6847; sprint_report.py:1618.
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint close` renders its end-of-run summary from `sprint_report` before `--apply-signoff` runs, and the harness token capture (`retro accuracy --tokens-from-harness`, sprint.py:6842-6847) sits INSIDE apply-signoff. So the COST block reads from a velocity row that does not exist yet and prints 'not attributable - no per-run figure was captured for this close' (`sprint_report.py`:1618), in the same command that is about to capture the figure. RUN-01M2JA6J closed reporting not attributable; running the same capture by hand immediately afterwards returned 6,459,675 tokens and 62,715 per point from data that was already on disk - the baseline stamped at run open (4,271,975) against the session meter (10,842,294). The measurement was never missing; the report just asked before the answer was written. Every interactive close has the same ordering, so the velocity table's actual column has been empty by construction rather than by absence of data.

## Steps to Reproduce

1. Close a run with --apply-signoff. 2. Read the COST block in the close's summary: 'not attributable'. 3. Run `retro.py accuracy --id <retro> --tokens-from-harness --write` by hand. 4. It captures a figure from the baseline and the session meter, both of which were on disk when the close printed.

## Proposed Fix

Capture the token actual BEFORE the summary is rendered, or render the summary after apply-signoff completes. The second is the direction RFC0059 takes anyway: every fact is frozen before the report is produced, and the report is the last thing generated. Until then the close's own summary cannot describe the run it just closed.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint close` renders its end-of-run summary from `sprint_report` before `--apply-signoff` runs, and the harness token capture (`retro accuracy...
- [ ] **AC2** The proposed fix lands, pinned by a test: Capture the token actual BEFORE the summary is rendered, or render the summary after apply-signoff completes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Filed |
