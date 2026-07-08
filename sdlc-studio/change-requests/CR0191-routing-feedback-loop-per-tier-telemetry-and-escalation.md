# CR-0191: Routing feedback loop: per-tier telemetry and escalation recording

> **Status:** Proposed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** P3
> **Type:** feature-request
> **RFC:** RFC-0026 (WS3)
> **Depends on:** CR-0189

## Summary

`telemetry.py` FIELDS gains `tier_recommended`, `tier_delivered`, `model`, `escalated`
(with matching `record` CLI args), and `show --summary` additionally groups critic-verdict
mix and reopen rate per `tier_delivered` - the per-tier escape rate is both the routing
calibration signal and the benchmark's quality axis. Escalations append a ledger entry
(existing ledger.py; model-instructed prose, no ledger code change).

## Acceptance Criteria

- [ ] `telemetry record` accepts and persists tier_recommended/tier_delivered/model/escalated; absent fields stay omitted (whitelist discipline unchanged)
- [ ] `telemetry show --summary` reports verdict mix and reopen rate grouped by tier_delivered when any record carries it; no per-tier block when none do
- [ ] reference-sprint.md's close step documents recording tier fields + the escalation ledger entry
- [ ] test_telemetry.py covers the new fields and the per-tier grouping

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | RFC0026 WS3 | Created via `new` (deterministic) |
