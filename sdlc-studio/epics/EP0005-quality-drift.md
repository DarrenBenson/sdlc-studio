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

**Estimated Story Count:** 4

## Story Breakdown

- [x] [US0001: Census-based reconcile with scoped auto-fix](../stories/US0001-reconcile-census-autofix.md)
- [x] [US0002: Executable AC verification with verify gate](../stories/US0002-verify-ac-gate.md)
- [x] [US0003: Unified review with modified-since detection and cadence](../stories/US0003-review-cadence.md)
- [x] [US0004: Status dashboard and single-step hint](../stories/US0004-status-hint.md)
- [x] [US0012: Referential-integrity check](../stories/US0012-referential-integrity-check.md) (CR0003, determinism sprint)
- [x] [US0014: review_prep staleness determinism](../stories/US0014-review-prep-determinism.md) (CR0004, determinism sprint)
- [x] [US0019: verify_ac report history and dry-run record](../stories/US0019-verify-ac-report-history.md) (CR0005, backlog-closeout)
- [x] [US0020: verify_ac graded (eval) verifier verb](../stories/US0020-verify-ac-graded-verifier.md) (CR0006, backlog-closeout)
- [x] [US0022: checks emit remediation guidance](../stories/US0022-checks-remediation-guidance.md) (CR0025, remediation)
- [x] [US0023: reconcile apply - mechanical index fixes](../stories/US0023-reconcile-apply.md) (CR0026, RFC0003)
- [x] [US0025: conformance adoption cutoff](../stories/US0025-conformance-adoption-cutoff.md) (CR0027, consuming repo A)
- [x] [US0028: decompose apply_type (refactor-first)](../stories/US0028-decompose-apply-type.md) (CR0030, RFC0009 signal)
- [x] [US0029: validate no-ac honours the adoption cutoff](../stories/US0029-validate-no-ac-adoption-cutoff.md) (CR0031, consuming repo A)

> Deterministic next-ID allocation (US0005) is owned by EP0008 (Tooling &
> Scripts), not this epic.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield); worked-example stories generated |
