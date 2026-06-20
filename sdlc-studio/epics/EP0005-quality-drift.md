# EP0005: Quality & Drift Control

> **Status:** Ready
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --

## Summary

The control plane that keeps artifacts true to code: census-based reconciliation,
executable acceptance-criteria verification, the unified review (including a CODE
leg) with cadence, and the status/hint dashboards. This epic is backed by real,
unit-tested Python scripts, so its stories carry implementation-ready,
test-validatable acceptance criteria - the strongest demonstration of generate
mode in this backlog.

**PRD Reference:** [Reconcile / Verify AC](../prd.md#3-feature-inventory)

## Scope

### In Scope

- `reconcile` (scripts/reconcile.py): census, drift detection, auto-fix, `--scope`, `--verify`.
- `verify_ac` (scripts/verify_ac.py): AC DSL, per-AC verdicts, verify gate, JSON report.
- `review` (scripts/review_prep.py): unified doc + CODE review, modified-since detection, cadence.
- `status` / `hint` (scripts/status.py): pipeline dashboard and single next step.

### Out of Scope

- The completion cascades themselves are defined in `reference-outputs.md` and triggered by EP0003/EP0007; this epic *detects and repairs* missed cascades.

### Affected Personas

- **Orchestrator:** runs reconcile/review at cadence boundaries.
- **AI Agent:** uses verify_ac as the "Done" oracle.

## Acceptance Criteria (Epic Level)

- [ ] `reconcile` reconstructs state from a file census and fixes mechanical drift without auto-transitioning judgement calls.
- [ ] `verify_ac` reports `Verified: yes/no` per AC and supports a blocking verify gate.
- [ ] `review` detects artifacts modified since last review and enforces the cadence (incl. CODE leg).
- [ ] `status`/`hint` report pipeline health and the next actionable step.
- [ ] All four scripts are pure stdlib, read-only over the workspace, and unit-tested.

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| None | -- | -- | -- |

## Sizing

**Estimated Story Count:** 5

## Story Breakdown

- [ ] [US0001: Census-based reconcile with scoped auto-fix](../stories/US0001-reconcile-census-autofix.md)
- [ ] [US0002: Executable AC verification with verify gate](../stories/US0002-verify-ac-gate.md)
- [ ] [US0003: Unified review with modified-since detection and cadence](../stories/US0003-review-cadence.md)
- [ ] [US0004: Status dashboard and single-step hint](../stories/US0004-status-hint.md)
- [ ] [US0005: Deterministic next-ID allocation](../stories/US0005-next-id-allocation.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield); worked-example stories generated |
