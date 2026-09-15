# BG0685: project_upgrade reads plan-review verdicts with no kind, so a repair-plan APPROVE counts as a repair story's spec review

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py
> **Evidence:** BG0673 round-2 and round-4 QA plan reviews, 2026-09-15 (pre-existing).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`project_upgrade.py` (around line 678) calls the plan-review lookup without a kind, so once repair-plan verdicts exist (BG0673) a repair-plan APPROVE is read as the unit's spec review during rebaseline.

## Steps to Reproduce

Record a repair-plan APPROVE on a repair story, then run the rebaseline path; it reads the unit as spec-reviewed.

## Proposed Fix

Pass kind='spec' (or the kinds the rebaseline means) explicitly.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `project_upgrade.py` (around line 678) calls the plan-review lookup without a kind, so once repair-plan verdicts exist (BG0673) a repair-plan APPROVE is read...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Record a repair-plan APPROVE on a repair story, then run the rebaseline path; it reads the unit as spec-reviewed.
- [ ] **AC3** The proposed fix lands, pinned by a test: Pass kind='spec' (or the kinds the rebaseline means) explicitly.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
