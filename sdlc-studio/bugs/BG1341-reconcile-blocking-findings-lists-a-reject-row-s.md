# BG1341: reconcile.blocking_findings lists a REJECT row's RULINGS item as a blocking defect in a lane brief's file history

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, changelog.d/BG1341.md
> **Evidence:** RUN-01M77177, 2026-11-12: BG1030's builder
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:18:59Z

## Summary

BG1030 stores rulings as a `RULINGS:` item on the verdict row. `reconcile.blocking_findings`, which feeds the 'blocking defects their reviews found' section of every lane brief, still reads that item as a blocking finding.

## Steps to Reproduce

Record a REJECT whose block has a RULINGS line, then print a lane brief for a unit sharing its files.

## Proposed Fix

Skip the RULINGS item in `blocking_findings` as `parse_findings` does.

## Acceptance Criteria

- [ ] **AC1** Given a REJECT row carrying a RULINGS item beside one blocking finding, when `blocking_findings` reads it, then only the blocking finding is listed. Fails on: the rulings text listed as a defect.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::BlockingFindingsTests::test_a_rulings_item_is_not_a_blocking_finding
  - **Verified:** yes (2026-11-12)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
