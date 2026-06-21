# CR-0050: telemetry record + .local/telemetry.jsonl schema (RFC0014 WS1)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Feature
> **Requester:** Darren Benson (RFC decision session)
> **Date:** 2026-06-21
> **Affects:** scripts/telemetry.py (new)
> **Depends on:** RFC0014
> **GitHub Issue:** --

## Summary

A deterministic `telemetry record` that appends a per-unit run outcome to a gitignored `.local/telemetry.jsonl` (local-only, no upload): {id, type, iterations, wall_time_s, stages, critic_verdict, complexity, churn, reopened}.

## Proposed Changes

- `scripts/telemetry.py record` appends one JSONL record; pure stdlib; tokens recorded only when passed in.
- `.local/telemetry.jsonl` (gitignored); no network.

## Acceptance Criteria

- [x] `telemetry record` appends a well-formed JSONL line with the declared fields; a missing optional field is omitted, never errors.
- [x] Nothing leaves the machine (no network call).
- [x] Unit-tested where code; independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0050) | Complete - US0036: telemetry.py recorder; created+closed by the tool (dogfood); critic REJECT->fixed (gitignored path) |
| 2026-06-21 | Darren Benson | Raised - RFC decision session |
