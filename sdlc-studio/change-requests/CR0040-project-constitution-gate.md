# CR-0040: optional project constitution + machine-checkable principle gate (RFC0005)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Feature
> **Requester:** Darren Benson
> **RFC:** RFC-0005
> **Date:** 2026-06-20
> **Affects:** scripts/constitution.py (new), templates/constitution.md (new), templates/config-defaults.yaml, reference-doctrine.md, reference-scripts.md, SKILL.md, sdlc-studio/constitution.md (dogfood)
> **Depends on:** CR0027 (project_override / config), CR0003 (integrity), CR0023 (conformance)
> **GitHub Issue:** --

## Summary

Delivers RFC0005 (Option A, scoped). An optional `sdlc-studio/constitution.md` lets a
project declare inviolable principles; `constitution check` asserts the
machine-checkable ones across the artifact graph. Each checkable principle carries a
`` `rule:` `` from a fixed vocabulary that MAPS onto the existing deterministic checks
(integrity / conformance / validate / reconcile) - one consolidated gate, not a new
engine. Free-text principles are advisory (loaded as a generation constraint, listed,
not gated). Enforcement is advisory by default; `constitution.enforce: true` makes a
violation fail the check.

## Proposed Changes

- `scripts/constitution.py`: parse constitution.md + `check` gate (6-rule vocabulary
  reusing existing detectors); advisory/enforce semantics; degrades when absent.
- `templates/constitution.md`: the seed (principles + rule vocabulary + the
  adopt_after caveat); `sdlc-studio/constitution.md`: this repo's own (dogfood).
- `config-defaults.yaml`: `constitution.enforce: false`.
- Docs: `reference-doctrine.md#constitution`, `reference-scripts.md`, SKILL.md router row.

## Acceptance Criteria

- [x] `constitution check` asserts each declared checkable principle (6-rule vocabulary, each mapping onto integrity/conformance/validate/reconcile) and reports violations; advisory principles are listed, not gated.
- [x] Advisory by default (exit 0 with violations); `constitution.enforce: true` makes a violation exit non-zero; degrades safely when no constitution.md / no PyYAML / malformed config.
- [x] Each rule fires on a real violation and is silent when satisfied (unit-tested per rule); unknown / bare-prose `rule:` does not misclassify.
- [x] Dogfooded (this repo passes 5 gated principles); proven against consuming repo A (8 findings) and consuming repo B (139) read-only; independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0005) | Complete - constitution.py gate + template + dogfood; critic APPROVE (regex hardening + per-rule tests applied) |
