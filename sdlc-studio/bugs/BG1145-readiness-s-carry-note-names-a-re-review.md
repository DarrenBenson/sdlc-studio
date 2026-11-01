# BG1145: readiness's carry note names a re-review that critic.py record refuses for a unit at the cap with no filed carry bug; only a --ruling discharges it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, BG1140 APPROVE by qa-seat-BG1140-r1 (brief efc4a9bd1fa2).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T01:49:34Z

## Summary

qa-seat-BG1140-r1's APPROVE of BG1140 (2026-11-01) found the note's route is wrong for one shape. For a unit holding an unanswered REJECT whose verifiers pass, BG1140's readiness note says 'carried: re-review by <id> ... brief that reviewer ... --rejoinder' (readiness.py:983-987). But when the unit is at the review cap and `carried_by` is None (no carry bug was filed), `critic.round_refusal` (critic.py:1783-1798) refuses that reviewer's APPROVE: 'A unit still rejected at the cap is carried as a known issue, not reviewed again'. The only exit is `critic.py record --ruling DNNNN` (BG1003). AC1's cap test (`test_readiness.py`:636-644) pins exactly this state with a note naming a route that cannot be taken. This is not a regression, and no live unit is affected today.

## Steps to Reproduce

1. In a throwaway project, record two REJECTs by qa-r1 on a unit whose verifiers pass, with no carry bug filed.
2. `readiness.py check --id <unit>`: ready, note 'carried: re-review by qa-r1'.
3. `critic.py record --unit <unit> --verdict approve --reviewer qa-r1 ...`: exit 2, refused at the cap.

## Proposed Fix

When the unit is at the cap and `carried_by` is None, have the note name the operator ruling (`critic.py record --ruling DNNNN`) rather than a plain re-review. Give the cap test a real carry drop, so its fixture matches the route the note names.

## Acceptance Criteria

- [ ] **AC1** A unit at the cap with no filed carry bug gets a note naming `critic.py record --ruling`, and the note's route records cleanly in a fixture.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py
- [ ] **AC2** A unit under the cap, or carried with a filed carry bug, keeps the re-review note (the positive control).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py

## Impact

For that shape the operator is sent down a route that refuses, which is BG1140's own failure class.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
