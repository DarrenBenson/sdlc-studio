# BG0268: sprint plan leaves a stale sprint-plan.json and forecast record when a concurrent writer opens a run between the pre-check and open_run

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by the closing adversarial review of RUN-01KY5Y3W. US0326 gives `sprint plan --write` two guards against fusing a disjoint batch into an open run: a pure `disjoint_refusal()` pre-check in `cmd_plan`, and `open_run` itself raising `DisjointBatchError`. run-state.json is byte-identical after a refusal - the AC1 guarantee holds and was verified. But `cmd_plan` writes the forecast record (`record_forecast)` and `sprint-plan.json` BEFORE it calls `open_run`. If a concurrent writer opens a run in the window between the pre-check and `open_run`, the second guard correctly raises and the command exits non-zero, but by then the forecast record and sprint-plan.json for the refused plan have already been written and are left behind on the losing side of the race. Narrow: it needs two same-repo planners racing. Self-healing: the next successful plan overwrites both. So Low, and a follow-up rather than a repair round - but the run-state's byte-identical guarantee is not matched by the sibling artefacts.

## Steps to Reproduce

1. Reach the point in `cmd_plan` just after the `disjoint_refusal` pre-check passes. 2. Have a concurrent process open a disjoint run. 3. Let `cmd_plan` proceed: `open_run` raises, the command exits 2, but sprint-plan.json and the forecast record for the refused plan are on disk. Expected: either the sibling writes happen only AFTER `open_run` succeeds, or they are rolled back on the `open_run` refusal, so a refused plan leaves nothing behind, matching run-state.json's guarantee.

## Proposed Fix

Order the writes so the forecast record and sprint-plan.json are written only AFTER `open_run` returns successfully - `open_run` is the authority on whether the plan may proceed, so nothing a plan produces should be persisted before it says yes. Alternatively wrap the plan-write path in the same advisory lock `open_run` uses, so the pre-check and the open are one critical section.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Filed |
