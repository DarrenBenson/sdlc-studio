# CR-0540: Low-severity crs (consolidated)

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-08-09
> **Consolidation:** low-severity-crs
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio-authoring-session; human; v1

## Summary

A themed consolidation of Low-severity findings that individually do not warrant a standalone artefact (triage noise control, schema v3). Triage the batch, then action or reject as one.

## Impact

Each finding here is Low-severity on its own; the batch is triaged, then actioned or rejected as one. Left unconsolidated, the same findings would each mint an artefact and drown the real signal.

**Points:** 3

## Consolidated Findings

- **the epic-close test-plan gate asks for a plan that restates its stories' already-reviewed ones**: Closing EP0211 required a `## Test Plan` and an independent plan-review verdict of kind `test-plan` on the EPIC, though all eight of its stories had already carried their own test plans, each plan-reviewed by a seat before its code was written. The epic plan I wrote to satisfy the gate names the same eight mutants those unit plans already name, because there is nothing else true to write. The gate's own rationale - reviewing the test costs a fraction of reviewing the code - was paid at unit level and cannot be paid twice.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio-authoring-session | Consolidation opened |
