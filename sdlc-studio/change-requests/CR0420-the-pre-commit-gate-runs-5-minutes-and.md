# CR-0420: the pre-commit gate runs ~5 minutes and its budget advisory reports +200% over a stale baseline on every commit, so the signal has become noise rather than a bound anyone acts on

> **Status:** In Progress
> **Decomposed-into:** EP0161
> **Created:** 2026-07-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/.config.yaml, tools/gate_timing.py
> **Priority:** Medium
> **Type:** Feature
> **Size:** M

## Summary

Every commit that touches scripts/ prints 'gate-budget: OVER - ~309s of a 120s budget (baseline 99s on 2026-07-21, +210% since)'. The gate is genuinely ~5 minutes (unit suites ~190s, whole gate ~300s), the baseline is weeks stale, and the advisory fires green every time - so it neither bounds the cost nor prompts action. Either re-budget deliberately against current reality, or reduce the cost (split/parallelise the suites, skip unaffected lanes), so the number means something again.

## Impact

Every committer on this repo. A budget line that is always red is a broken instrument: it stops being read, which is worse than no budget, and the underlying ~5-minute gate is a real per-commit tax that keeps growing as the suites grow.

## Acceptance Criteria

- [ ] AC1: a normal scripts-touching commit no longer prints a gate-budget OVER line - the baseline reflects the current measured cost, or the budget is re-derived deliberately with the reason recorded
- [ ] AC2: if the cost is reduced instead of re-budgeted, the reduction is measured and the new time recorded, so the improvement is evidenced not asserted
- [ ] AC3: the budget line distinguishes a genuine regression from steady growth already accounted for, so it bounds something rather than firing on every commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-25 | sdlc-studio | Created via `new` (deterministic) |
