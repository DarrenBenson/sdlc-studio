# US0065: Triage status vocabulary and gated transitions recording triaged_by

> **Status:** Ready
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0014
> **Persona:** Orchestrator / Operator
> **Source:** CR-0173 (workstream 1)

## User Story

**As an** operator moving from gate to auditor
**I want** triage as explicit, agent-performable status transitions that record triaged_by
**So that** the sampling human has a defined surface to audit and separation-of-duties has its trigger

## Acceptance Criteria

### AC1: Inbox then gated triaged transition

- **Given** a newly filed artefact in `inbox`
- **When** an agent triages it
- **Then** `transition.py` gates the `triaged` transition, requires structured triaged_by, and
  enforces the separation-of-duties rule at that moment
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k triage_gate

### AC2: Triage severity recorded alongside the raiser's

- **Given** a triaging persona assigning severity
- **When** the transition records
- **Then** both the raiser's and triager's severity are retained for later metrics
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k triage_severity

## Design Notes (groomed 2026-07-08, see D0015)

- **Era-gated:** the `inbox`/`triaged` vocabulary is active only under `schema_version: 3`
  (dormant on main; v2 projects keep their current `STATUS_VOCAB` and filing defaults).
- **Vocab shape (findings only):** prepend `inbox` before the existing first state on
  `cr`/`bug`/`rfc` in `STATUS_VOCAB` (`sdlc_md.py`); `triaged` maps onto the existing first
  workflow state (`Open` / `Approved` / `In Review`) rather than adding a second new state.
  `story`/`epic` are unchanged (authored, not triaged).
- **Filing default:** under v3, `artifact.py` files findings into `inbox`, not
  `Proposed`/`Open`. Guard this behind the era check so v2 defaults are untouched.
- **Transition gate:** `transition.py` gates `inbox -> triaged`, requires structured
  `triaged_by` (CR0169), and enforces CR0170 separation-of-duties at that moment.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | sdlc | Groomed to Ready: vocab shape + era-gating settled (D0015) |
