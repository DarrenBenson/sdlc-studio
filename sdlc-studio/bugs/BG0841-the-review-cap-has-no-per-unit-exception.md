# BG0841: The review cap has no per-unit exception path, so an operator-granted extra round can only land by force

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap_exception.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/BG0841.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Sprint 6 RUN-01M3HR74, BG0818 round 3 (D0285, D0286), 2026-09-28
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T17:45:57Z

## Summary

BG0818's bounded round 3 was granted by the operator (D0285) and APPROVED by the reviewer who rejected it, yet critic.py record refuses any verdict past `review.max_rounds` ('record refused ... at the cap of 2') and transition refuses Fixed while the last recorded verdict is a REJECT. The only exit was transition --force, recorded in D0286, so the verdict ledger holds two REJECTs and no APPROVE for a unit that passed review. The cap is right as a default; it has no way to honour a recorded operator exception for one unit.

## Steps to Reproduce

Record two REJECTs for a unit; the cap carries it; record a third verdict from the same reviewer: refused.

## Proposed Fix

Let critic.py record accept one further round for a unit named by an accepted operator decision (for example --exception D0285, checked against decisions.md), writing the round with that decision id so the ledger and the Done/Fixed gate read it; without such a decision the cap refuses as today.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0818's bounded round 3 was granted by the operator (D0285) and APPROVED by the reviewer who rejected it, yet critic.py record refuses any verdict past...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Record two REJECTs for a unit; the cap carries it; record a third verdict from the same reviewer: refused.
- [ ] **AC3** The proposed fix lands, pinned by a test: Let critic.py record accept one further round for a unit named by an accepted operator decision (for example --exception D0285, checked against decisions.md)...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
