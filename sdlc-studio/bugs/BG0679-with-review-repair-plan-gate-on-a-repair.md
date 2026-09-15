# BG0679: With review.repair_plan_gate on, a repair bug set straight to Closed or Verified skips the gate

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** BG0673 round-4 QA plan review, 2026-09-15 (probed at HEAD: Open -> Closed rc 0).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The repair-plan gate (being wired by BG0673) binds at Fixed and Done only; transition.py takes a non-production bug from Open straight to Closed with rc 0, so a gated repair unit can bypass the gate by skipping Fixed. `sdlc_md.is_delivered_terminal` (Fixed, Verified, Closed) is the predicate that would close it.

## Steps to Reproduce

1. After BG0673 lands, set `review.repair_plan_gate`: on.
2. `transition.py set --id <repair bug> --status Closed` with no plan: rc 0.

## Proposed Fix

Bind the gate on `is_delivered_terminal` rather than the Fixed/Done pair; pin Closed and Verified.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The repair-plan gate (being wired by BG0673) binds at Fixed and Done only; transition.py takes a non-production bug from Open straight to Closed with rc 0, so...
- [ ] **AC2** The proposed fix lands, pinned by a test: Bind the gate on `is_delivered_terminal` rather than the Fixed/Done pair; pin Closed and Verified.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
