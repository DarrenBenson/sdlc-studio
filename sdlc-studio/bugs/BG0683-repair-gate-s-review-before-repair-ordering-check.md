# BG0683: repair_gate's review-before-repair ordering check (US0312 AC4) is dead on the wired path

> **Status:** Superseded
> **Closes with:** US0913 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/repair_plan.py, .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py
> **Evidence:** BG0673 rounds 2-4 and BG0678 rounds 1-2 plan reviews, 2026-09-15 (reported, untracked).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`repair_gate` carries a clause requiring the plan review to precede the repair; BG0673 wires the gate and BG0678 keeps its rounds, but neither pins the ordering, and no id carries it, so the clause is unreachable from any command.

## Steps to Reproduce

Read `repair_plan.repair_gate`'s ordering clause, then grep for a caller or test reaching it through transition.py: none.

## Proposed Fix

Pin the ordering through the wired transition: a repair recorded before its plan's approval is refused.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `repair_gate` carries a clause requiring the plan review to precede the repair; BG0673 wires the gate and BG0678 keeps its rounds, but neither pins the...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read `repair_plan.repair_gate`'s ordering clause, then grep for a caller or test reaching it through transition.py: none.
- [ ] **AC3** The proposed fix lands, pinned by a test: Pin the ordering through the wired transition: a repair recorded before its plan's approval is refused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0913 ships - planning: SUPERSEDED - repair_gate ordering: repair ledger deleted in batch 2; superseded only once US0913 ships (D0264) |
| 2026-09-25 | sdlc-studio BG0772 | Superseded under D0264: its closing story US0913 is Done (BG0772) |
