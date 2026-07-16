# CR-0259: RFC0034 D3: a sprint capacity budget in tokens/wall-clock, wired to CR0225 appetite

> **Status:** Complete
> **Size:** M
> **Priority:** P3
> **Type:** Feature
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-config.md
> **Depends on:** CR0258

## Summary

The capacity half of RFC0034. An operator-set per-sprint budget in tokens + wall-clock, so the plan-time 'does this batch fit' and the run-time circuit-breaker (CR0225 appetite: --appetite-minutes / --appetite-units) are the same number rather than two disconnected limits. sprint plan reports the batch's estimated size against the budget and flags an over-budget batch at plan time (not mid-run). Ships with a provisional default; recalibrates off the D4 velocity history once it exists.

## Impact

The operator gets a plan-time 'this batch is too big' signal instead of discovering it when CR0225's breaker halts the run mid-sprint. Plan capacity and run appetite stop being two separate numbers that can disagree.

**Effort:** M

## Acceptance Criteria

- [ ] `sprint plan` reports the batch's estimated size against the configured token and wall-clock
      budget, and a batch that exceeds it is flagged AT PLAN TIME - the operator is told before
      the run starts, not when the breaker halts it mid-sprint.
- [ ] The capacity budget feeds CR0225's appetite defaults: one configured number, two consumers
      (plan-time fit and run-time breaker), so the two limits cannot disagree.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
