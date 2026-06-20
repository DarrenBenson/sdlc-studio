# EP0003: Implementation & Planning

> **Status:** Ready
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --

## Summary

Turn a Ready story into working code: produce an implementation plan, execute it
under TDD, and manage the Claude Code plan-file lifecycle. The single-story,
full-fidelity path (PL + TS + WF artifacts) that the agentic modes compress.

**PRD Reference:** [Feature Inventory](../prd.md#3-feature-inventory)

## Scope

### In Scope

- `code plan` - implementation plan for a story (edge-case discovery, audit trail).
- `code implement` - execute the plan, TDD-gated.
- Plan-file lifecycle: list / archive (`reference-plan-files.md`).

### Out of Scope

- Test spec / automation (EP0004).
- Agentic batch implementation (EP0007).

### Affected Personas

- **AI Agent:** executes the plan.
- **Orchestrator:** reviews plans for single-story or audit-sensitive work.

## Acceptance Criteria (Epic Level)

- [ ] `code plan` produces a PL artifact with phases and edge cases.
- [ ] `code implement` follows TDD (failing test first) and updates status through the flow.
- [ ] Completion triggers the Story Completion Cascade (EP0005).
- [ ] Plan files are listable and archivable.

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| EP0002 | Epic | Ready | Darren Benson |

## Sizing

**Estimated Story Count:** 4

## Story Breakdown

- [ ] US: Code plan generation
- [ ] US: Code implement (TDD)
- [ ] US: Plan-file lifecycle (list/archive)
- [ ] US: Story status flow + cascade trigger

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
