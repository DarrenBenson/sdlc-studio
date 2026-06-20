# EP0001: Requirements Artifacts

> **Status:** Ready
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --

## Summary

The requirements layer of the pipeline: authoring or reverse-engineering the
project-level documents that everything downstream traces back to - PRD, TRD,
TSD, personas - plus the persona consultation model (consult / chat / Three
Amigos). Both create and generate modes.

**PRD Reference:** [Feature Inventory](../prd.md#3-feature-inventory)

## Scope

### In Scope

- PRD create + generate (`reference-prd.md`).
- TRD create + generate, optional modules (diagrams, containers, ADR).
- TSD (project-level test strategy).
- Personas create + generate (`reference-persona-generate.md`).
- Consult / chat / workflow-personas (Three Amigos pressure-test).

### Out of Scope

- Epic/story decomposition (EP0002).
- The review *cadence* over these documents (EP0005).

### Affected Personas

- **Orchestrator:** authors or extracts the founding documents.
- **Consuming-project Developer:** runs generate mode against their codebase.

## Acceptance Criteria (Epic Level)

- [ ] PRD, TRD, TSD, personas each support create and (where applicable) generate mode.
- [ ] Generate-mode outputs are migration-blueprint depth with confidence markers.
- [ ] Project-level docs are exempt from lifecycle status checks per `reference-outputs.md`.
- [ ] Consultation produces persona feedback recorded against the artefact.

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| None | -- | -- | -- |

## Sizing

**Estimated Story Count:** 6

## Story Breakdown

- [ ] US: PRD create/generate
- [ ] US: TRD create/generate (+ modules)
- [ ] US: TSD
- [ ] US: Personas create/generate
- [ ] US: Consult / pressure-test canvas
- [ ] US: Interactive persona chat

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
