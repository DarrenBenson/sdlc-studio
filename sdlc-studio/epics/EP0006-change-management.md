# EP0006: Change Management (CR/RFC/Bug)

> **Status:** Done
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --

## Summary

Handle change after the PRD is set: RFCs explore unsettled design and spawn CRs;
CRs propose and action change into epics/stories; bugs track defects with
hypothesis discipline. The lifecycle this very brownfield run exercises (RFC0001
lives here).

**PRD Reference:** [Feature Inventory](../prd.md#3-feature-inventory)

## Scope

### In Scope

- CR lifecycle: propose, `cr action` (into epics/stories), `cr sync` (GitHub).
- RFC lifecycle: draft, review, accept (spawns CRs), record ADR in TRD.
- Bug lifecycle: open through verified/closed, hypothesis discipline.

### Out of Scope

- The epics/stories a CR spawns are owned by EP0002.

### Affected Personas

- **Orchestrator:** decides RFC vs CR vs ADR; triages bugs.

## Acceptance Criteria (Epic Level)

- [ ] RFC weighs >=2 options, resolves Open Decisions, then spawns linked CRs.
- [ ] CR actions into epics/stories and optionally syncs to a GitHub Issue.
- [ ] Bug status flow enforced; root cause not guessed (hypothesis discipline).
- [ ] Accepted RFC stays the living design home its CRs reference.

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| EP0001 | Epic | Ready | Darren Benson |

## Sizing

**Estimated Story Count:** 3

## Story Breakdown

- [ ] US: CR lifecycle + cr action
- [ ] US: RFC lifecycle + spawn CRs
- [ ] US: Bug tracking + hypothesis discipline
- [x] [US0021: rfc decide - multi-RFC decision session](../stories/US0021-rfc-decide-session.md) (CR0024)

> GitHub Issue sync for CR/story/epic is owned by EP0008 (Tooling & Scripts);
> this epic consumes it as a cross-epic dependency.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
