# CR-0021: Autosprint tranche-audit step (pre-flight grooming)

> **Status:** In Progress
> **Priority:** High
> **Type:** Feature
> **Requester:** Darren Benson
> **Date:** 2026-06-20
> **Affects:** reference-autosprint.md, help/autosprint.md, scripts/audit.py (new), scripts/integrity.py (CR0003, reused), RFC0001
> **Depends on:** CR0003 (referential integrity - reused as the link-integrity lens)
> **GitHub Issue:** --

## Summary

The autosprint loop selects and orders a batch, then goes straight to the triage
STOP. But a batch is often not fit to work: CRs carry tautological or empty AC (the
BG0003 vacuous-pass class), depend on unfinished work, or are already
delivered/superseded. Today that is caught only by an operator noticing mid-flow
(as happened in the determinism sprint - CR0016 sharpening, CR0018 already done).
Add a defined **tranche-audit** step between `plan` and the triage STOP that grooms
each unit for readiness, so the operator approves a clean, verifiable batch.

## Problem

There is no gate on tranche readiness. The conformance check (CR/WS7) is per-story
and post-delivery; nothing audits the *incoming* batch. Weak AC defeat the verify
and conformance gates downstream (they pass vacuously), unmet dependencies cause
mid-run stalls, and already-terminal items waste a unit of work.

## Proposed Changes

### Item 1: Tranche-audit workflow step

**Priority:** High **Effort:** Low

Add step 2 "Tranche audit" to `reference-autosprint.md` (and the `help`): after the
batch is selected, each unit is groomed - sharpen weak AC, close already-terminal
items, flag-and-defer blocked ones - and the findings feed the triage STOP and the
decisions ledger. The adversarial lens (is the problem still real, the change still
sound) delegates to RFC0002's audit when built; until then it is model-instructed.

### Item 2: Deterministic readiness helper

**Priority:** High **Effort:** Medium

A `scripts/audit.py` that, given a batch (CR/bug ids or a query), emits a JSON
readiness report flagging per unit: **weak-AC** (placeholder/tautology or no
checkable AC), **unmet-deps** (`Depends on` not satisfied), **already-terminal**
(Complete/Superseded/Done), and **link-integrity** (reuses CR0003's
`scripts/integrity.py`). Non-zero exit when any unit is not ready.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| reference-autosprint.md | New step 2 "Tranche audit" | Modified |
| help/autosprint.md | Document the step | Modified |
| scripts/audit.py | Deterministic readiness report | New |
| scripts/integrity.py | Reused as the link-integrity lens (CR0003) | Reused |

### Breaking Changes

None. A new pre-flight step and helper; the loop is unchanged downstream.

## Acceptance Criteria

- [ ] `audit.py` flags a CR with tautological/empty AC as `weak-AC`, and a CR with concrete AC as ready.
- [ ] It flags a unit whose `Depends on` is unsatisfied as `unmet-deps`, and an already-Complete/Superseded unit as `already-terminal`.
- [ ] It reuses `integrity.py` for link-integrity and emits a JSON readiness report; non-zero exit when any unit is not ready. Unit-tested.
- [ ] `reference-autosprint.md` documents the tranche-audit step between `plan` and the triage STOP.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Raised - tranche readiness should be a defined loop step, not improvised mid-flow (determinism-sprint lesson) |
