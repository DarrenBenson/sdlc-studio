# CR-0290: TRD §6 data architecture is a workflow behind committed main: no issue type, no story Blocked status, no inbox triage lane, no two-backlog model - inside its own declared coverage

> **Status:** Complete
> **Decomposed-into:** EP0071
> **Priority:** Medium
> **Type:** docs
> **Size:** M
> **Affects:** sdlc-studio/trd.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

The TRD's `ARTIFACT_TYPES` table lists 8 types; the code registry has 9 including `issue` (IS prefix, its own 7-state vocabulary). The TRD's story vocabulary omits 'Blocked', which the code includes (shipped in v4.1.0, inside coverage). Entirely absent: the schema-v3 inbox triage lane (`FINDING_TYPES`/`INBOX_STATUS`/`TRIAGE_TARGET)` and the whole two-backlog architecture (REQUEST/DISCOVERY/PRODUCT type sets, `two_backlog_enforced` with G1 plan-refuse and G2 derived-terminal gates, Parent:/Decomposed-into: link primitives, link-asymmetry reconciliation) - committed on main in 8fdddc6, and §1 explicitly claims coverage of unreleased main. Panel softened two sub-claims (the coverage line enumerates four named workstreams; the freshness guard was never 'falsified' since it pins fixed strings) but the drift itself verified 3x, and the repo's precedent (CR0184/CR0252) is that a TRD-refresh CR is exactly what gets filed.

## Impact

The TRD's `ARTIFACT_TYPES` table lists 8 types; the code registry has 9 including `issue` (IS prefix, its own 7-state vocabulary).

## Acceptance Criteria

- [ ] §6's type registry includes issue with its directory, prefix and status vocabulary
- [ ] The story status vocabulary includes Blocked
- [ ] The inbox triage lane on findings is documented (types, statuses, triage targets)
- [ ] The two-backlog model gets a §6 subsection: request/discovery/product type sets, `two_backlog.enforce` and its G1/G2 gates, Parent:/Decomposed-into: primitives and their reconciliation

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
