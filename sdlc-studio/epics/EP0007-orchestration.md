# EP0007: Agentic Orchestration

> **Status:** Ready
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --

## Summary

Drive whole epics and projects: dependency-ordered execution, agentic wave
analysis with subagent fan-out, compressed status flow, and blocking quality
gates at wave/epic/project boundaries. This is the inner machinery RFC0001's
autonomous loop wraps.

**PRD Reference:** [Feature Inventory](../prd.md#3-feature-inventory)

## Scope

### In Scope

- `project plan` / `project implement` with dependency graph + resume.
- `epic implement --agentic` wave analysis and execution.
- Compressed agentic status flow; per-wave/epic/project quality gates.
- Agentic lessons accumulation and wave-prompt templates.

### Out of Scope

- The outer autonomous control loop (RFC0001, not yet built).

### Affected Personas

- **Orchestrator:** launches and supervises runs.
- **AI Agent:** executes waves with isolated context.

## Acceptance Criteria (Epic Level)

- [ ] Epics execute in dependency order; circular deps abort with the cycle named.
- [ ] Agentic waves fan out parallelisable stories; gates run at boundaries.
- [ ] `project-state.json` tracks progress and supports `--resume`.
- [ ] Quality gates (typecheck + tests + reconcile) are blocking, not advisory.

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| EP0002 | Epic | Ready | Darren Benson |
| EP0003 | Epic | Ready | Darren Benson |
| EP0005 | Epic | Ready | Darren Benson |

## Sizing

**Estimated Story Count:** 4

## Story Breakdown

Autosprint (RFC0001) is this epic's centrepiece; Phase 1 delivered:

- [x] [US0007: Lifecycle-conformance check](../stories/US0007-lifecycle-conformance-check.md)
- [x] [US0008: Autosprint batch selector and ordering](../stories/US0008-autosprint-batch-selector.md)
- [ ] US: Project plan (dependency graph + wave estimate)
- [ ] US: Project implement (resume, commit/reconcile/review checkpoints)
- [ ] US: Epic agentic wave execution
- [ ] US: Quality gates + agentic lessons

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
