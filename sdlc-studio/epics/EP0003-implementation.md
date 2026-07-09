# EP0003: Implementation & Planning

> **Status:** Done
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --


> **Founding epic - closed 2026-07-09.** Every capability below is delivered in the shipped skill (v4.0.0-rc.1); the suite (1455 tests) and the working `/sdlc-studio` commands demonstrate it. The unlinked `US:` breakdown items are early placeholder stubs from before stories were individually tracked - complete in the implementation, not as separate story artefacts. Closed for status hygiene; no capability is outstanding.

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

- [x] `code plan` produces a PL artifact with phases and edge cases.
- [x] `code implement` follows TDD (failing test first) and updates status through the flow.
- [x] Completion triggers the Story Completion Cascade (EP0005).
- [x] Plan files are listable and archivable.

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| EP0002 | Epic | Ready | Darren Benson |

## Sizing

**Estimated Story Count:** 4

## Story Breakdown

- [x] US: Code plan generation
- [x] US: Code implement (TDD)
- [x] US: Plan-file lifecycle (list/archive)
- [x] US: Story status flow + cascade trigger

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
