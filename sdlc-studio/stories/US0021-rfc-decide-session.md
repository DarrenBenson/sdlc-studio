# US0021: rfc decide - multi-RFC decision session

> **Status:** Done
> **Epic:** [EP0006: Change Management (CR/RFC/Bug)](../epics/EP0006-change-management.md)
> **Owner:** Autosprint (CR0024, rfc-decide)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** operator
**I want** a decision session that triages the whole Draft RFC backlog at once
**So that** accept/defer/withdraw across many RFCs is a defined function, not an
improvised pass (CR0024) - the front-of-pipe analogue of the tranche-audit.

## Context

Implements CR0024. New `scripts/rfc.py decide` digests Draft/In-Review RFCs into
decision-readiness data (open decisions total + Open, workstreams, has-recommendation,
`ready_for_decision`); `reference-rfc.md` + `help/rfc.md` document the session
workflow (digest -> brief -> batch accept/defer/withdraw, routing accept to the
existing `rfc accept`). The adversarial judgement stays model-instructed.

## Acceptance Criteria

### AC1: Per-RFC readiness digest

- **Given** a Draft RFC with N open-decision rows (M still Open) and W workstreams
- **When** `digest(root)` runs
- **Then** the RFC's entry reports `open_decisions=N`, `open_count=M`, `workstreams=W`, and `has_recommendation`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rfc.py::DigestTests::test_ready_when_recommendation_and_no_open
- **Verified:** no (2026-07-20)

### AC2: ready_for_decision reflects open decisions + recommendation

- **Given** an RFC with an Open decision, or with no recommendation
- **When** the digest runs
- **Then** `ready_for_decision` is false; a Draft with a recommendation and no Open decisions is true
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rfc.py::DigestTests::test_not_ready_with_open_decisions
- **Verified:** yes (2026-06-20)

### AC3: JSON digest + decidable filter

- **Given** a workspace with Draft and Accepted RFCs
- **When** `rfc.py decide --format json` runs
- **Then** it emits `{rfcs, summary}` JSON (Draft/In-Review only by default) and exits 0
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rfc.py::CliTests::test_decide_json
- **Verified:** yes (2026-06-20)

### AC4: Session documented

- **Given** the RFC references
- **When** searched
- **Then** `reference-rfc.md` documents a `decide` decision-session action
- **Verify:** grep "## decide" .claude/skills/sdlc-studio/reference-rfc.md
- **Verified:** yes (2026-07-10)

## Implementation

`scripts/rfc.py`: `digest()` (section + table parsing) + `decide` CLI. Docs in
`reference-rfc.md#decide` and `help/rfc.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0024) | Decomposed from CR0024 (rfc-decide) |
