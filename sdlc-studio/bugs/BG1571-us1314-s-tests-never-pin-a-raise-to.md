# BG1571: US1314's tests never pin a raise to a middle class, a story with several Affects files, the open-status scope, or the silent skip of a stamp apply cannot rewrite

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile_risk_class.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Evidence:** US1314 QA verdict, run sixteen, 2026-11-17.
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T23:57:57Z

## Summary

The QA review of US1314 (run sixteen, APPROVE) killed 10 of 16 mutants. The survivors show four untested edges of the new risk-class drift kind: a raise to the map's class when that class is elevated rather than the top class, a story whose several Affects files map to different classes, the rule that only open stories are rewritten, and apply skipping without a word a stamp it cannot rewrite.

## Steps to Reproduce

Read sdlc-studio/reviews/verdicts/US1314/9b9eb601e44e-a75a487a.txt; apply the six surviving mutants it lists to reconcile.py and run `test_reconcile_risk_class.py.`

## Proposed Fix

Add one test per edge; make apply print the stamp it could not rewrite.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The QA review of US1314 (run sixteen, APPROVE) killed 10 of 16 mutants.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read sdlc-studio/reviews/verdicts/US1314/9b9eb601e44e-a75a487a.txt; apply the six surviving mutants it lists to reconcile.py and run...
- [ ] **AC3** The proposed fix lands, pinned by a test: Add one test per edge; make apply print the stamp it could not rewrite.

## Impact

A later change to the drift kind could raise to the wrong class or rewrite a closed story with the tests still green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
