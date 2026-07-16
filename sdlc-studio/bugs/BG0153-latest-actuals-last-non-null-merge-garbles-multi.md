# BG0153: latest_actuals' last-non-null merge garbles multi-record cost: a reopen-reclose second record overwrites the first cycle's tokens, and a merged flat+attempts bucket makes accuracy() and unit_cost() disagree

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

Two defects with one root cause: `latest_actuals` (telemetry.py:428-452) merges records per-field, last-non-null, with no cross-record aggregation. (1) transition.py:507-509 explicitly blesses a reopen-then-reclose as 'honestly a second cycle' producing a second record, so the second cycle's tokens REPLACE the first cycle's; `sprint_report` then prints 'Cost (rework included): N tokens' having silently dropped the first cycle's spend - the exact cheap-first-escalated figure US0173 exists to expose (`retro._worker_hours` has the same defect for `wall_time_s).` (2) A legacy flat record followed by an attempts-only re-record yields a bucket carrying BOTH stale flat tokens and the new attempts list; accuracy() (retro.py:585-595) is flat-first while `unit_cost()`/`attempts_of` is attempts-first, so the estimate-vs-actual ratio reports the stale figure while the spend report prices the attempts sum - precisely the 'two honest subsystems contradicting' the retro.py:585 comment claims the fallback prevents. Tests cover only the attempts-only and bare-close shapes. Six panel votes, all not-refuted.

## Steps to Reproduce

(1) `telemetry record --id US0001 --tokens 50000 --model haiku`; reopen; `telemetry record --id US0001 --tokens 80000 --model opus` -> `latest_actuals` bucket {tokens: 80000, model: opus}; `sprint_report` renders 'Cost (rework included): 80,000' - the 50,000 haiku cycle vanished. (2) Flat record {tokens: 50000, model: haiku} then attempts-only record {attempts: [{opus, 200000}]} -> merged bucket carries both; retro accuracy() reports `actual_tokens`=50000 while `unit_cost` prices 200000.

## Proposed Fix

Define one cross-record cost semantics in `latest_actuals`: aggregate cost-bearing fields across a unit's records (e.g. convert each flat record to an implicit attempt and concatenate attempts lists) so rework sums instead of overwriting; make accuracy() and `unit_cost()` share one precedence (attempts-first - identical for legacy records via the implicit-attempt shim); apply the same treatment to `retro._worker_hours` for `wall_time_s`; add tests for two-flat-cycles and flat-then-attempts shapes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
