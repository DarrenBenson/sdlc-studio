# CR-0051: loop writes a telemetry record per unit close (RFC0014 WS2)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Requester:** Darren Benson (RFC decision session)
> **Date:** 2026-06-21
> **Affects:** reference-autosprint.md, scripts/transition.py / close cascade
> **Depends on:** RFC0014, CR0050
> **GitHub Issue:** --

## Summary

Wire the autosprint/close cascade to call `telemetry record` when a unit reaches a terminal status, so run data accrues automatically.

## Proposed Changes

- The close cascade records iterations, wall-time, stages passed, and the critic verdict on each unit close.
- Documented in reference-autosprint.md.

## Acceptance Criteria

- [ ] Closing a unit appends a telemetry record; the loop never fails if telemetry recording fails (guarded).
- [ ] Unit-tested where code; independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - RFC decision session |
