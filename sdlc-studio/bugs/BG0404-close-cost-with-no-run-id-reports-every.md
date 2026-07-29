# BG0404: close_cost with no run id reports every close ever recorded as this one: 6x on seconds, 143x on elapsed

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Measured on this workspace: close_cost(root, 'RUN-01KYNKDP') = 221s over 3 runs, 10m41s elapsed; close_cost(root, None) = 1355s over 17 runs, 1529m06s elapsed - printed verbatim as one close's cost.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`close_cost` filters `run_id is None or r.get('run_id') == run_id`, so a None run id short-circuits the filter and includes every close row ever recorded. `cmd_close` proceeds on any truthy state, and a state carrying no `run_id` is exactly the case `record_content_review`'s new guard exists for - so the close can print whole-project totals as its own cost.

A cost report whose stated purpose is measurement honesty over-reports by 6x on seconds and 143x on elapsed.

Separately, a cross-run reuse cannot be resolved: `by_at` is built from rows already filtered to this run, while `reusable_close_verdict` scans the whole ledger regardless of run - which is the only reuse that saves seconds a PREVIOUS run paid for. A measured 96s saving is reported as `UNMEASURED ... whose source run is not on the ledger`, with the source row two lines above it.

## Steps to Reproduce

1. `close_cost(root, None)` on any workspace with several recorded closes - it sums them all.
2. Record a full close row under RUN-A and a reuse under RUN-B pointing at it; `close_cost(root, 'RUN-B')` reports the saving as unknown.

## Proposed Fix

Treat a missing run id as UNANSWERABLE rather than as 'every run': report the cost as not attributable and say why, which is the direction every other figure in this function already degrades in. Resolve `reused_from` against the WHOLE ledger, since that is the set `reusable_close_verdict` draws from.

## Acceptance Criteria

- [ ] A close with no run id reports its cost as not attributable, naming why, rather than summing every close on the ledger.
- [ ] A reuse whose source row is on the ledger under another run resolves, and its saved seconds are reported.
- [ ] A reuse whose source genuinely is not on the ledger is still reported UNMEASURED rather than zero.

## Impact

The close's cost line is the number the next reduction is measured against, and CR0498 exists because that number was previously an impression. A figure 143x too large is worse than none: it makes any real saving invisible and any real regression unremarkable.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
