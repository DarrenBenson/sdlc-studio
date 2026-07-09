# EP0002: Decomposition (Epics & Stories)

> **Status:** Done
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --


> **Founding epic - closed 2026-07-09.** Every capability below is delivered in the shipped skill (v4.0.0-rc.1); the suite (1455 tests) and the working `/sdlc-studio` commands demonstrate it. The unlinked `US:` breakdown items are early placeholder stubs from before stories were individually tracked - complete in the implementation, not as separate story artefacts. Closed for status hygiene; no capability is outstanding.

## Summary

Decompose requirements into epics and then into user stories with
implementation-ready acceptance criteria. Includes `story generate` - the
reverse-engineering path that extracts real validation rules, error messages and
API contracts from code rather than from epic descriptions.

**PRD Reference:** [Feature Inventory](../prd.md#3-feature-inventory)

## Scope

### In Scope

- Epic decomposition from PRD, with engineering/product/test perspectives.
- Story creation from epic AC, and `story generate` from code.
- Story Ready criteria + quality checklist enforcement.

### Out of Scope

- Implementation planning (EP0003).
- Completion cascades and drift fixes (EP0005).

### Affected Personas

- **Orchestrator:** decomposes the backlog.
- **AI Agent:** consumes story AC as the unit of work.

## Acceptance Criteria (Epic Level)

- [x] Epics map back to PRD features via the Feature Inventory Epic column.
- [x] Stories carry implementation-ready AC (concrete values, exact error messages, API contracts).
- [x] `story generate` extracts behaviour from code, not just epic text.
- [x] Story Ready criteria validated before promotion (`reference-decisions.md`).

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| EP0001 | Epic | Ready | Darren Benson |

## Sizing

**Estimated Story Count:** 4

## Story Breakdown

- [x] US: Epic decomposition + perspectives
- [x] US: Story creation from epics
- [x] US: Story generate (brownfield extraction)
- [x] US: Ready-criteria + quality gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
