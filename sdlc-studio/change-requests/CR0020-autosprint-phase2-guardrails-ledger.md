# CR-0020: Autosprint Phase 2 - deterministic guardrails, decisions ledger, autonomous wiring

> **Status:** In Progress
> **Priority:** High
> **Type:** Feature
> **Requester:** Darren Benson
> **Date:** 2026-06-20
> **Affects:** scripts/ledger.py (new), scripts/loop_guard.py (new), reference-autosprint.md, reference-project.md, help/autosprint.md, RFC0001
> **Depends on:** RFC0001 (Accepted), US0007 conformance, US0008 batch selector
> **GitHub Issue:** --

## Summary

RFC0001 Phase 1 shipped the usable autosprint cut (batch selector, conformance
gate, policy doc, command wiring). Phase 2 adds the hard guardrails the
loop-engineering consensus says the model cannot supply itself: a persisted
decisions ledger (D4/WS5), deterministic loop guardrails - iteration cap,
repetition-breaker, completion oracle (D5/WS3) - and the `--autonomous` mode that
wires them together with the independent-critic policy (WS6/WS4). Delivered by
driving autosprint over itself (the loop self-hosting).

## Problem

The Phase-1 loop leans on the existing wave engine plus the conformance gate and
the triage STOP. Three judgements remain model-instructed that RFC0001 says must be
deterministic or persisted:

- **Am I stuck?** No cap or repetition-breaker - a unit can thrash indefinitely.
- **Am I done?** No batch-level completion oracle distinct from per-unit conformance.
- **Decisions survive compaction?** No persisted ledger - rulings live in context and
  are re-litigated after a reset.

## Proposed Changes

### Item 1: Decisions ledger (D4 / WS5)

**Priority:** High **Effort:** Low

A committed, append-only per-tranche ledger under `sdlc-studio/decisions/`. A
`scripts/ledger.py` records a ruling (timestamp, decision, rationale) and reads the
ledger back, so decisions survive context compaction and resume. Append-only (open
in append mode; never truncate). Becomes US0009.

### Item 2: Deterministic loop guardrails (D5 / WS3)

**Priority:** High **Effort:** Medium

A `scripts/loop_guard.py` with three pure, unit-tested mechanisms the model cannot
skip: an **iteration cap** (N failed green attempts per unit), a
**repetition-breaker** (same failure signature R times), and a **completion oracle**
(all batch units terminal: Done or Blocked). On cap/repetition a unit is
quarantined - marked **Blocked**, logged, the run continues (D2). State persists to
`sdlc-studio/.local/loop-state.json` (run-local, like `project-state.json`). Becomes
US0010.

### Item 3: `--autonomous` wiring + independent critic (WS6 / WS4)

**Priority:** Medium **Effort:** Low

Document the unattended `--autonomous` mode on `reference-project.md` /
`reference-autosprint.md` / `help/autosprint.md`: it ties the ledger, the
guardrails, the per-unit loop (decompose -> TDD -> verify -> conformance ->
independent non-author critic -> green commit), quarantine-and-continue, and the
mandatory closing reconcile + review. The critic (D3/WS4) stays a model-instructed
loop step. Becomes US0011.

## Impact Assessment

### Affected Modules

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/ledger.py | Persisted decisions ledger | New |
| scripts/loop_guard.py | Cap, repetition-breaker, completion oracle | New |
| reference-autosprint.md | `--autonomous` mode, ledger + guardrail steps | Modified |
| reference-project.md | `--autonomous` note on `project implement` | Modified |
| help/autosprint.md | `--autonomous` flag | Modified |
| RFC0001 | Phase-2-delivered status | Modified |

### Breaking Changes

None. New scripts and documented mode; Phase-1 behaviour unchanged.

## Acceptance Criteria

- [ ] `ledger.py` appends rulings to a committed per-tranche file and reads them back; append-only.
- [ ] `loop_guard.py` quarantines a unit at the cap or on a repeated signature, and the completion oracle reports all-terminal.
- [ ] Both scripts are unit-tested; `npm test` green.
- [ ] `--autonomous` mode is documented end to end, tying ledger + guardrails + critic + closing gate.
- [ ] The conformance check passes on the new EP0007 stories (the loop gating its own delivery).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Raised - RFC0001 Phase 2 (guardrails, ledger, autonomous wiring); actioned via autosprint |
