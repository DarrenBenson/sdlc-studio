# BG0052: telemetry is never recorded by the delivery loop: transition-to-terminal bypasses artifact close

> **Status:** Closed
> **Verification depth:** functional (4 unit tests + live: this bug's own close writes the first records)
> **Severity:** medium
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

reference-sprint.md: 'On each unit close (artifact close), a telemetry event ... is appended to sdlc-studio/.local/telemetry.jsonl'. The actual delivery loop closes units via transition.py set (Done/Complete/Closed) - artifact close was never invoked across three full sprints (~20 units closed today), so telemetry.jsonl is empty and the new telemetry show --summary (RFC0018) has nothing to summarise. The calibration data the feature exists for silently never accumulates; a seam between two tools that both legitimately 'close' a unit.

## Steps to Reproduce

1. Deliver a unit the loop's way: transition.py set --id CRxxxx --status Complete. 2. Check sdlc-studio/.local/telemetry.jsonl - no record. 3. telemetry show --summary reports 0 records after a fully-delivered sprint.

## Proposed Fix

Either transition.py records the telemetry event when the target status is terminal for the type (id, type, and any --iterations/--verdict passed through), or the sprint reference and conformance guidance mandate artifact close as the ONLY close path and transition refuses terminal statuses without it. Prefer the former: transition is where the loop already is, and telemetry must never require a second call to be remembered (the CR0136 decorative-field lesson). Unit test: a terminal transition appends exactly one record; non-terminal appends none.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Filed |
| 2026-07-04 | operator | Review: CONFIRMED (transition.py mentions telemetry 0 times, artifact close 8; telemetry.jsonl never written). Priority of the batch - a dead feature, the product_reconcile disease class. Fix direction endorsed: record on terminal transition, never require a second call |
| 2026-07-04 | claude | Fixed: transition records the telemetry event on terminal transitions (id/type + passed-through --iterations/--wall-time-s/--verdict); never on dry-run/non-terminal. Tests seen RED first. This close is the repo's first recorded event |
