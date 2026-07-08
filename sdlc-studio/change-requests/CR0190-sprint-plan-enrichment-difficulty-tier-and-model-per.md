# CR-0190: Sprint plan enrichment: difficulty, tier and model per unit

> **Status:** Complete
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** P2
> **Type:** feature-request
> **RFC:** RFC-0026 (WS2)
> **Depends on:** CR-0189

## Summary

`sprint.py plan` extracts its per-unit enrichment (currently WSJF-only: complexity +
token_budget) into a helper that runs for BOTH `priority` and `wsjf` orders, and extends it
via route.py: `difficulty` (always emitted, advisory), `tier` + `model` (only when
`routing.enabled`). Estimator failure degrades to no routing fields - never breaks planning.
Routing policy + escalation prose lands in `reference-sprint.md` (advisory; overrides go to
the ledger; retry once at assigned tier then escalate one declared tier within loop_guard's
unchanged 3-attempt cap; repeated identical failure signature at sub-max tier escalates once
instead of quarantining). `reference-agent-prompt-template.md` gains a `#tier-routing`
consumption section (prompt contract byte-identical across tiers). Doc coverage:
reference-scripts.md, scripts/README.md, help/sprint.md.

## Acceptance Criteria

- [ ] `sprint.py plan` emits `difficulty` for every unit under both orders; `tier`/`model` appear only when routing.enabled in config
- [ ] With routing disabled the plan JSON is unchanged from today apart from the added `difficulty` field
- [ ] An estimator exception on one unit degrades that unit to no routing fields and the plan still completes
- [ ] reference-sprint.md documents the routing policy, floors, escalation rule and the override-goes-to-ledger rule
- [ ] reference-agent-prompt-template.md#tier-routing documents orchestrator consumption; prompt contract unchanged across tiers
- [ ] test_sprint.py covers both orders with and without routing enabled

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | RFC0026 WS2 | Created via `new` (deterministic) |
